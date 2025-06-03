import json
import os
from typing import Dict, List, Any

class TemplateGenerator:
    def __init__(self, idl_path: str, output_dir: str):
        with open(idl_path, 'r') as f:
            self.idl = json.load(f)
        self.output_dir = output_dir
        self.program_name = self.idl['metadata']['name']
        self.program_name_lower = self.program_name.lower()

    def generate_environment_class(self) -> str:
        return f'''import * as anchor from '@coral-xyz/anchor';
import {{ {self.program_name} }} from "../target/types/{self.program_name_lower}";

export class Environment {{
    provider: anchor.AnchorProvider;
    program: anchor.Program<{self.program_name}>;
    admin: anchor.web3.Keypair;

    constructor() {{
        try {{
            // Read admin keypair from JSON file
            const adminKeypairFile = require('./admin.json');
            this.admin = anchor.web3.Keypair.fromSecretKey(
                new Uint8Array(adminKeypairFile)
            );
        }} catch (e) {{
            console.warn("Could not load admin keypair from file, generating new one");
            this.admin = anchor.web3.Keypair.generate();
        }}
    }}
}}'''

    def generate_init_env(self) -> str:
        return f'''import * as anchor from '@coral-xyz/anchor';
import {{ Environment }} from './environment';
import {{ {self.program_name} }} from "../target/types/{self.program_name_lower}";
import * as utils from './utils';
import * as constants from './constants';

export async function initEnviroment(test_env: Environment) {{
    const provider = anchor.AnchorProvider.env();
    anchor.setProvider(provider);
    test_env.provider = provider;
    test_env.program = anchor.workspace.{self.program_name} as anchor.Program<{self.program_name}>;

    // Initialize your program-specific accounts here
    // Example:
    // test_env.config = utils.get_pda(['config'], test_env.program.programId);
}}
'''

    def generate_constants(self) -> str:
        return '''export const INITIAL_SOL_BALANCE = 500;

// Add your program-specific constants here
// Example:
// export const CONFIG_SEED = 'config';
'''

    def generate_utils(self) -> str:
        return '''import * as anchor from '@coral-xyz/anchor';

export async function airdrop(
    connection: any,
    address: any,
    amount = 500_000_000_000
) {
    await connection.confirmTransaction(
        await connection.requestAirdrop(address, amount),
        'confirmed'
    );
}

// Template for PDA creation
export function get_pda(
    seeds: Buffer[],
    program_id: anchor.web3.PublicKey,
): anchor.web3.PublicKey {
    const [pda, bump] = anchor.web3.PublicKey.findProgramAddressSync(
        seeds,
        program_id
    );
    return pda;
}

// Example of program-specific PDA getter
// export function get_config(
//     program_id: anchor.web3.PublicKey,
// ): anchor.web3.PublicKey {
//     return get_pda(
//         [Buffer.from('config')],
//         program_id
//     );
// }

export function delay(ms: number) {
    return new Promise(resolve => setTimeout(resolve, ms));
}'''

    def generate_main_test_file(self) -> str:
        return f'''import {{ Environment }} from "./environment";
import {{ initEnviroment }} from "./init-env";
import {{ test1 }} from "./test1";
import {{ test2 }} from "./test2";

describe("{self.program_name}", () => {{
    const test_env = new Environment();
    before('Prepare', async () => {{
        await initEnviroment(test_env);
    }});
    describe('Test1', async () => {{
        test1(test_env);
    }});
    describe('Test2', async () => {{
        test2(test_env);
    }});
}});'''

    def generate_test_scenario(self, scenario_number: int) -> str:
        instructions = self.idl.get('instructions', [])
        instruction_tests = []
        for inst in instructions:
            name = inst['name']
            accounts = [acc['name'] for acc in inst['accounts']]
            accounts_str = ', '.join(accounts)
            instruction_tests.append(f'''    it("{name}", async () => {{
        // Add your test logic here
        // Example:
        // await test_env.program.methods.{name}().accountsPartial({{
        //     {accounts_str}
        // }}).signers([test_env.admin]).rpc({{ commitment: 'confirmed', "skipPreflight": true }});
    }});''')

        return f'''import {{ Environment }} from './environment';
import * as anchor from '@coral-xyz/anchor';
import * as constants from './constants';
import * as utils from './utils';

export async function test{scenario_number}(test_env: Environment) {{
{chr(10).join(instruction_tests)}
}}'''

    def generate_all(self):
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)

        # Generate files
        files = {
            'environment.ts': self.generate_environment_class(),
            'init-env.ts': self.generate_init_env(),
            'constants.ts': self.generate_constants(),
            'utils.ts': self.generate_utils(),
            'testing.ts': self.generate_main_test_file(),
            'test1.ts': self.generate_test_scenario(1),
            'test2.ts': self.generate_test_scenario(2)
        }

        for filename, content in files.items():
            with open(os.path.join(self.output_dir, filename), 'w') as f:
                f.write(content)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Generate test templates from IDL')
    parser.add_argument('idl_path', help='Path to the IDL file')
    parser.add_argument('output_dir', help='Output directory for generated files')
    args = parser.parse_args()

    generator = TemplateGenerator(args.idl_path, args.output_dir)
    generator.generate_all()
    print(f"Generated test templates in {args.output_dir}")

if __name__ == '__main__':
    main()
