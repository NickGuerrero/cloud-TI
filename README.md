# General Purpose Slack Application for the CTI Community

## Description
This repository contains the pubilcly available portions of the Slack application used on the Computing Talent Initiative (CTI) Slack workspace. The CTI community is a network of undergraduate students trying to build a career in tech, and the goal of this application is to provide useful tools and services for the student community. Primarily built on Python with Slack's Bolt API, the application is hosted on an AWS EC2 instance, with Docker organizing the runtime environment.

## Contributing
Contributors should be affliated with the CTI community, as one of the main goals of the project is to have an open-source project that students can contribute to. General GitHub rules and etiquette apply, but briefly:
1. Fork the repository and make changes changes there
2. Once ready, pull request into the **test** branch for review
   - Be descriptive to all changes made in your branch, especially if you're merging a lot commits
3. Code will be reviewed and tested (if applicable) before moving to testing with a private Slack workspace.
4. Once successful, code will be moved to the main branch and used in the next update.

Other various rules:
- No tabs, all non-commented code should have 4-space indents.
- When adding features with Slack blocks, please place block formatting in the folder *modals*. Avoid cluttering the code.
- When adding functions to *utils*, please add accompanying test cases to verify that they'll work.
- When adding libraries to any requirements.txt, make sure that the libraries and versions are specified in the commit as well.
- The *logs* and *sql* folders should be empty, apart from the README's. Don't change the .gitignore without permission.

This isn't an exhaustive list, but should give an idea of what to expect when making pull requests. 

## Project Directory:

    cloud-ti
    ├── app
    |   ├── slack-listener (Slack bolt listener that responds to SLack events)
    |   ├── grouping-queue (Service for taking handling server requests)
    |   ├── modals (Slack blocks used for formatting responses)
    |   ├── utils (Supplementary functions that can run outside a container)
    |   ├── sql (Directory for SQL scripts)
    |   ├── logs (Directory for storing logs)
    |   └── .env (Not available on GitHub, but here for reference)
    ├── test (Test files go here)
    ├── docker-compose.yml
    └── README.md

Please file any suggestions, comments, or complaints to the issues board