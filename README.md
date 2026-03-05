# MathMex

MathMex is a web application designed to assist users with mathematical queries and provide solutions using advanced search capabilities powered by OpenSearch and machine processing. This project consists of a backend built with Flask and a frontend developed using React.

## Project Structure

```
mathmex/
├── apps/
│   ├── backend/     # Flask API server
│   ├── db/          # OpenSearch index management and data pipeline
│   └── frontend/    # React user interface
├── bin/             # Server management scripts (run, stop, install)
└── data/            # Raw TSVs, vector .npy files, and generated .jsonl files (gitignored)
```

### Backend

The backend is responsible for handling API requests and interacting with OpenSearch.  
See [`apps/backend/README.md`](apps/backend/README.md) for setup and usage instructions.

### DB

The `db` app contains everything needed to set up and populate the OpenSearch database: index schemas, admin scripts (create/delete/clear), and the data processing pipeline.  
See [`apps/db/README.md`](apps/db/README.md) for details.

### Frontend

The frontend is a React application that provides the user interface for MathMex.  
See [`apps/frontend/README.md`](apps/frontend/README.md) for setup and usage instructions.

## Getting Started

### 1. Configuration

Copy the example files and fill in your values:

```sh
cp config.ini.example config.ini
cp .env.example .env
```

`config.ini` holds OpenSearch connection info, Flask settings, and the model path. `config.ini.example` includes public read-only credentials for the MathMex OpenSearch instance so you can test immediately without setting up your own database.

`.env` just points the backend at your `config.ini`:
```
BACKEND_CONFIG=/path/to/your/config.ini
```

### 2. Install and run

See the respective README files for each component:
- [`apps/backend/README.md`](apps/backend/README.md) — Flask API setup
- [`apps/frontend/README.md`](apps/frontend/README.md) — React app setup
- [`apps/db/README.md`](apps/db/README.md) — OpenSearch index and data pipeline

## Contributing

Contributions are welcome! To contribute to MathMex, please follow these steps:

1. **Fork the repository**  
   Click the "Fork" button at the top right of this page to create your own copy of the repository.  
   This creates your own copy of the MathMex repo under your GitHub account. You can freely make changes to this copy without affecting the original project.

2. **Clone your fork**  
   Open a terminal and run:  
   ```sh
   git clone https://github.com/your-username/MathMex.git
   ```
   This downloads your forked repo from GitHub to your local computer, so you can work on the code locally.

3. **Create a new branch**  
   Navigate to the project directory and create a new branch for your feature or bugfix:  
   ```sh
   git checkout -b my-feature-branch
   ```
   Branches let you work on new features or bug fixes without affecting the main codebase. Creating a new branch keeps your changes organized and separate.

4. **Make your changes**  
   Implement your feature or fix the bug in your local code.  
   Adding tests is encouraged to ensure your changes work as expected.

5. **Commit your changes**  
   In the terminal run:
   ```sh
   git add .
   git commit -m "Describe your changes"
   ```
   You can save your changes to your local branch with a description message. This helps others understand what you changed and why.

6. **Push to your fork**  
   ```sh
   git push origin my-feature-branch
   ```
   This uploads your committed changes from your local branch to your forked repo on GitHub.

7. **Open a Pull Request**  
   Go to the original repository on GitHub and open a Pull Request from your branch.  
   You request that your changes be reviewed and merged into the original MathMex repo. It will be reviewed and discussed before any necessary changes are made before merging.

Please follow these steps to help keep the project organized and easy to maintain.

