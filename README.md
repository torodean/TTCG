# TTCG
A True TCG concept design.

## Website
https://truetradingcardgame.github.io/

## Overview
For a comprehensive overview of this project, please see the documentation in the `documenation` directory.

## Folders

### `bin`
- **Purpose**: This folder stores the main scripts and files used for effect and card generation.

### `documenation`
- **Purpose**: this folder contains the documenation for this project. This documentation is a work in progress and continually changing.

### `images`
- **Purpose**: this folder contains images used for this project.

## Scripts

### `commitAll.sh`
- **Purpose**: This is just a helper script for quick git committing.
- **Key Features**: This script takes a commit message as an argument and then performs the following commands:
  - `git add -A`
  - `git commit -m $1`
  - `git push`
- **Usage**: To use this script, simply run it with `./commitAll.sh <commit_message>`.

### `ttcg-setup.sh`
- **Purpose**: This script will setup the needed packages for the TTCG project (still in dev).
- **Usage**: To use this script, simply run it with the following:
  - To make the script executable (if not already) run `chmod a+x ttcg-setup.sh`.
  - To run the script: `./ttcg-setup.sh`


## Contact

For all inquiries, comments, questions, suggestions, etc... Please contact us via the following email: truetradingcardgame@gmail.com 


## License

Copyright Antonius Torode, 2025. All rights reserved. This project is not open source and may not be used, copied, modified, or distributed without explicit permission from the author.
