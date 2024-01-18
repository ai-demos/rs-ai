## ReachSuite AI

This repo contains the code for running the ReachSuite AI in 2 environments:

1. `dev`: A development environment running locally on docker
2. `prd`: A production environment running on AWS ECS

## Setup Workspace

### 1. Clone the git repo and `cd rs-ai`

### 2. Create virtual env and install dependencies

```sh
./scripts/create_venv.sh
```

This script will:

- Create a virtualenv `aienv`
- Install project dependencies
- Install the `rs-ai` project in editable mode

### 3. Activate the virtual env:

```sh
source aienv/bin/activate
```

<details>
<summary>How to create the virtual env manually</summary>

### To create the virtual env manually

- Create + activate a virtual env:

```sh
python3 -m venv aienv
source aienv/bin/activate
```

- Install `phidata`:

```sh
pip install phidata
```

</details>

### 4. Setup workspace:

```sh
phi ws setup
```

### 5. Copy `workspace/example_secrets` to `workspace/secrets`:

```sh
cp -r workspace/example_secrets workspace/secrets
```

### 6. Copy the `.env` file and set your `OPENAI_API_KEY`

```sh
cp example.env .env
```

## Local ReachSuite AI

### 1. Install [docker desktop](https://www.docker.com/products/docker-desktop)

### 2. Test the anonymizer from the command line

```sh
python ai/test/anonymizer.py
```

### 3. Start the workspace using:

```sh
phi ws up
```

### 4. Test the Anonymizer API

- Open [localhost:8000/docs](http://localhost:8000/docs) to view the FastApi docs.

- Test the `/v1/anonymize/request` with the json from: https://gist.github.com/ashpreetbedi/f9209c9455f31a9c455a1e35947a4f89

### 5. Stop the workspace using:

```sh
phi ws down
```

## Formatting and Linting

- Format your code using

```sh
./scripts/format.sh
```

- Lint/Type check your code using

```sh
./scripts/validate.sh
```

## Build your own image

- Open `workspace/settings.py` file
- Update the `image_repo` to your image repository
- Set `build_images=True` and `push_images=True`

```python
ws_settings = WorkspaceSettings(
    ...
    # -*- Image Settings
    # Repository for images
    image_repo="your-image-repo",
    # Build images locally
    build_images=True,
    # Push images after building
    # push_images=True,
)
```

- Run `phi ws up` and it should build your image
- Run `phi ws up -f` to force build the image

## Run on AWS

The `workspace/prd_resources.py` file contains the AWS resources you need to run your app on AWS.

- Add 2 subnets to the `workspace/settings.py` file (required for ECS services)

```python
ws_settings = WorkspaceSettings(
    ...
    # -*- AWS settings
    # Add your Subnet IDs here
    subnet_ids=["subnet-xyz", "subnet-xyz"],
    ...
)
```

- Create AWS resources

```sh
phi ws up --env prd --infra aws
```

## More information:

- [Run the AI API on AWS](https://docs.phidata.com/templates/ai-api/run-aws)
- Read how to [manage the development application](https://docs.phidata.com/how-to/development-app)
- Read how to [manage the production application](https://docs.phidata.com/how-to/production-app)
- Read how to [add python libraries](https://docs.phidata.com/how-to/python-libraries)
- Read how to [format & validate your code](https://docs.phidata.com/how-to/format-and-validate)
- Read how to [manage secrets](https://docs.phidata.com/how-to/secrets)
- Add [CI/CD](https://docs.phidata.com/how-to/ci-cd)
- Read the [AI API guide](https://docs.phidata.com/templates/ai-api)
