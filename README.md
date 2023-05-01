# General Purpose Slack Application for the CTI Community

## Description
This repository contains the pubilcly available portions of the Slack application used on the Computing Talent Initiative (CTI) Slack workspace. The CTI community is a network of undergraduate students trying to build a career in tech, and the goal of this application is to provide useful tools and services for the student community. Primarily built on Python with Slack's Bolt API, the application is hosted on an AWS EC2 instance, with Docker organizing the runtime environment. The current project includes:
- A home page for displaying links and other relevant information
- A service for matching users for mock interview practice, including problem suggestions

## Project Directory

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
    ├── app_manifest.yml
    └── README.md

## Deployment
For deploying stand-alone, you'll need the following outside of this directory:
- A Slack workspace to install the application, and the permissions to install a bot
- A server with the ability to build and run docker containers (This application currently uses AWS EC2)

General instructions:
- Go to https://api.slack.com/ & create a new app using the app_manifest.yml
- Install the application, and navigate to the OAuth & Permissions section to get the bot token (Starts with xoxb)
- On the Basic Information page under App Credentials, take the signing secret
- Create a .env file in the app/ folder, with the values:
  - `SLACK_BOT_TOKEN`=Your bot token
  - `SLACK_SIGNING_SECRET`=Your signing secret
  - `STUDENT_HANDBOOK_LINK`=https://bit.ly/Accelerate-Student-Handbook
  - `CANVAS_LINK`=https://cti-courses.instructure.com/
  - `DEEP_WORK_SESSION_LINK`=https://docs.google.com/spreadsheets/d/1C8FLUGrIDRXRkBgvDsNOmqwcW4go4QwfNOxoytjDvEk/
  - `INTERVIEW_ROADMAP_LINK`=https://docs.google.com/document/d/e/2PACX-1vSvtciYphR3AbIGmjXLRtDh5ACwi6r69WXIxwuNQDeBMeeQFo6HanXpDMPOufZcDOiChngEFpK7suxW/pub
  - `MOCK_INTERVIEW_QUICK_GUIDE`=https://docs.google.com/document/d/1iiVqnL_H8LQ9hgYBHOKAEp7JM8v_bNJoB_zl77iiWFE/edit?usp=sharing
- Clone the repository to a server of your choosing (You'll need at least the app/ folder and docker-compose.yml)
- Launch the server with docker compose (`sudo docker compose up` on a fresh linux install)
  - By default, the server is hosted on port 3000. If you're using AWS, be sure that this port is accessible from the web, unless you decide to change it.
- Copy the public URL (and port) and paste it into the app manifest on the Slack API site (at both `request_url`'s)
  - For example, `request_url = http://URL:3000/slack/events`. This uses Slack Bolt, so you need to append `/slack/events`.
  - Currently, Slack Bolt Python supports only HTTP, without workarounds.
- With the request url set-up, verify the install. If everything worked, the link gets verified & the application is running on the server correctly.
There are probably issues with deployment, if you need help, file an issue and I'll see if I can clarify.

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

Please file any suggestions, comments, or complaints to the issues board