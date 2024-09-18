# Solidity Contract Audit Service
## Overview
This Flask application provides a web interface to upload, analyze, and audit Solidity smart contracts. The application uses Slither for static analysis and GPT-4 for advanced audit results, including known vulnerabilities, best practices, and simplification of findings.
## Features
- **Upload Multi-file Contracts**: Upload multiple Solidity files at once, specifying the main contract.
- **Solidity Version Detection**: Automatically detects and uses the specified Solidity version in your contract.
- **Contract Flattening**: Flattens multi-file contracts into a single file.
- **Compilation**: Compiles the contract using solc.
- **Static Analysis with Slither**: Analyzes the contract using Slither.
- **Advanced Audit with GPT-4**: Provides detailed audit findings using OpenAI's GPT-4 model.
- **Styled Results**: Displays the audit results with severity-based formatting.