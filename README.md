# vCenter MCP Server

A Model Context Protocol (MCP) server for VMware vCenter that provides read-only access to vCenter resources including clusters, resource pools, and virtual machines.

## Features

- **Read-only access** to vCenter resources
- **Cloud Foundry deployment** support for Tanzu Cloud Foundry
- **Flexible credential management** via environment variables or Cloud Foundry service bindings
- **vCenter REST API integration** for all operations
- **FastMCP framework** for MCP protocol support
- **MVC architecture** following software design best practices
- **Comprehensive testing** with pytest
- **Type hints** throughout the codebase

## Supported Operations

1. **List all clusters** - Get all clusters in vCenter
2. **List VMs in cluster** - Get all virtual machines in a specific cluster
3. **List resource pools** - Get all resource pools in a specific cluster
4. **List VMs in resource pool** - Get all virtual machines in a specific resource pool
5. **Get vCenter status** - Get connection status and basic statistics

## Project Structure (MVC Architecture)

```
vcenter-mcp/
├── main/                           # Main application package
│   ├── __init__.py
│   ├── __main__.py                 # Application entry point
│   ├── server_factory.py           # Server creation and MVC initialization
│   ├── models/                     # Data models (M in MVC)
│   │   ├── __init__.py
│   │   └── vcenter_config.py       # Configuration and data models
│   ├── views/                      # Presentation layer (V in MVC)
│   │   ├── __init__.py
│   │   └── mcp_tools.py            # MCP tools and formatting
│   ├── controllers/                # Business logic (C in MVC)
│   │   ├── __init__.py
│   │   └── vcenter_controller.py   # Main controller
│   ├── services/                   # Service layer
│   │   ├── __init__.py
│   │   └── vcenter_service.py      # vCenter API service
│   └── config/                     # Configuration management
│       ├── __init__.py
│       └── config_manager.py       # Configuration and credentials
├── tests/                          # Test suite
│   ├── __init__.py
│   ├── test_config.py              # Configuration tests
│   └── test_mvc_structure.py       # MVC structure tests
├── app.py                          # Legacy entry point
├── test_connection.py              # Connection testing utility
├── config.env.example              # Environment configuration template
├── setup_env.py                    # Environment setup script
├── requirements.txt                # Python dependencies
├── setup.py                        # Package setup
├── pyproject.toml                  # Modern Python packaging
├── manifest.yml                    # Cloud Foundry manifest
├── Procfile                        # Cloud Foundry process
├── runtime.txt                     # Python runtime version
└── README.md                       # This file
```

## Architecture Overview

### MVC Pattern Implementation

- **Models** (`main/models/`): Data structures and configuration models
  - `VCenterConfig`: Configuration for vCenter connection
  - `Cluster`, `ResourcePool`, `VirtualMachine`: Data models for vCenter resources

- **Views** (`main/views/`): Presentation layer for MCP tools
  - `MCPToolsView`: Handles MCP tool registration and data formatting
  - Formats data for display to MCP clients

- **Controllers** (`main/controllers/`): Business logic and coordination
  - `VCenterController`: Main controller that coordinates between models and views
  - Handles data transformation and business rules

- **Services** (`main/services/`): Data access layer
  - `VCenterService`: Handles vCenter REST API interactions
  - Manages HTTP requests and responses

- **Config** (`main/config/`): Configuration management
  - `ConfigManager`: Handles credentials and environment configuration
  - Supports Cloud Foundry service bindings

- **Server Factory** (`main/server_factory.py`): Application initialization
  - `create_mcp_server()`: Creates and configures the MCP server
  - Handles proper MVC component initialization
  - Resolves circular import issues

## Prerequisites

- **Python 3.12+** (Required - tested with Python 3.12.3, Cloud Foundry uses python-3.12.*)
- VMware vCenter server with REST API access
- vCenter credentials (username/password)

## Installation

### Development Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd vcenter-mcp
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .
```

4. Install development dependencies:
```bash
pip install -e ".[dev]"
```

### Production Installation

```bash
pip install vcenter-mcp
```

## Configuration

### Environment Setup

The easiest way to set up your environment is using the provided setup script:

```bash
# Interactive setup
python setup_env.py

# View current configuration (passwords are masked)
python setup_env.py show
```

### Manual Environment Variables

Alternatively, you can manually set the following environment variables for vCenter access:

```bash
export VCENTER_HOST="https://your-vcenter-server.com"
export VCENTER_USERNAME="your-username"
export VCENTER_PASSWORD="your-password"

# Optional configuration
export VCENTER_VERIFY_SSL="true"  # Default: true
export VCENTER_TIMEOUT="30"       # Default: 30 seconds
export LOG_LEVEL="INFO"           # Default: INFO
```

### Using .env File

Create a `.env` file in the project root with the following content:

```bash
# Copy from config.env.example and update with your values
VCENTER_HOST=https://your-vcenter-server.com
VCENTER_USERNAME=your-username
VCENTER_PASSWORD=your-password
VCENTER_VERIFY_SSL=true
VCENTER_TIMEOUT=30
LOG_LEVEL=INFO
```

### Cloud Foundry Service Binding

Alternatively, you can bind to a vCenter service in Cloud Foundry. The service should provide credentials in the following format:

```json
{
  "host": "https://your-vcenter-server.com",
  "username": "your-username",
  "password": "your-password"
}
```

## Usage

### Command Line

Run the MCP server:

```bash
# Using the package
python -m main

# Using the console script (if installed)
vcenter-mcp

# Using the legacy entry point
python app.py
```

### Programmatic Usage

```python
from main.config.config_manager import ConfigManager
from main.controllers.vcenter_controller import VCenterController

# Get configuration
config_manager = ConfigManager()
config = config_manager.get_vcenter_config()

# Create controller and run MCP server
controller = VCenterController(config)
app = controller.create_mcp_server()
app.run()
```

### Testing Configuration

After setting up your environment, test your vCenter connection:

```bash
# Test connection and basic API calls
python test_connection.py

# View current configuration (passwords are masked)
python setup_env.py show
```

## Cloud Foundry Deployment

The application is configured for Cloud Foundry with flexible Python versioning:
- **Runtime**: `python-3.12.*` (allows automatic updates to any 3.12.x version)
- **Buildpack**: `python_buildpack`
- **Memory**: 256M
- **Disk**: 512M
- **Transport**: HTTP using FastMCP's async `http` transport (compatible with Spring AI WebMVC)
- **Health Check**: HTTP endpoint at `/health`

### Deploy to Tanzu Cloud Foundry

1. Login to your Cloud Foundry instance:
```bash
cf login -a https://api.your-cf-instance.com
```

2. Set the target organization and space:
```bash
cf target -o your-org -s your-space
```

3. Deploy the application:
```bash
cf push
```

### Environment Variables in Cloud Foundry

Set environment variables for vCenter access:

```bash
cf set-env vcenter-mcp-server VCENTER_HOST "https://your-vcenter-server.com"
cf set-env vcenter-mcp-server VCENTER_USERNAME "your-username"
cf set-env vcenter-mcp-server VCENTER_PASSWORD "your-password"
```

### Optional: Bind to vCenter Service

If you have a vCenter service available in your Cloud Foundry marketplace:

```bash
cf create-service vcenter-service standard vcenter-service
cf bind-service vcenter-mcp-server vcenter-service
```

## MCP Tools

The MCP server provides the following tools with proper names and descriptions for better discovery:

### 1. List Clusters (`list_clusters`)
**Description**: List all clusters in vCenter. Returns a formatted list of all available clusters with their names and IDs.

**Usage**:
```
list_clusters()
```

### 2. List VMs in Cluster (`list_vms_in_cluster`)
**Description**: List all virtual machines in a specific cluster. Requires the cluster name as input and returns a formatted list of VMs with their names and power states.

**Usage**:
```
list_vms_in_cluster(cluster_name: str)
```

### 3. List Resource Pools (`list_resource_pools`)
**Description**: List all resource pools in a specific cluster. Requires the cluster name as input and returns a formatted list of resource pools with their names and IDs.

**Usage**:
```
list_resource_pools(cluster_name: str)
```

### 4. List VMs in Resource Pool (`list_vms_in_resource_pool`)
**Description**: List all virtual machines in a specific resource pool. Requires the resource pool name as input and returns a formatted list of VMs with their names and power states.

**Usage**:
```
list_vms_in_resource_pool(resource_pool_name: str)
```

### 5. Get vCenter Status (`get_vcenter_status`)
**Description**: Get vCenter connection status and basic information. Returns connection status, host information, and counts of clusters, resource pools, and virtual machines.

**Usage**:
```
get_vcenter_status()
```

## MCP Client Connection

### Cloud Foundry Deployment
When deployed to Cloud Foundry, the MCP server is accessible via HTTPS transport:

- **URL**: `https://vcenter-mcp-server.apps.tas.tanzu.rocks` (port 443)
- **Transport**: `http` (async)
- **Protocol**: MCP over HTTPS

### Local Development
For local development, the server runs on:
- **Host**: `0.0.0.0` (default, configurable via `HOST` environment variable)
- **Port**: `8080` (default, configurable via `PORT` environment variable)
- **Transport**: `http` (async)

**Note**: Cloud Foundry sets the `PORT` environment variable for health checks, while external access is routed through HTTPS on port 443. The application must use the `PORT` environment variable to ensure health checks work correctly. The server defaults to port 8080 but can be overridden with the `PORT` environment variable.

## Development

### Python Version
This project requires **Python 3.12+** and has been tested with Python 3.12.3. For Cloud Foundry deployment, the runtime is set to `python-3.12.*` to allow automatic minor version updates.

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=main

# Run specific test file
pytest tests/test_mvc_structure.py
```

### Code Quality

```bash
# Format code
black main/ tests/

# Lint code
flake8 main/ tests/

# Type checking
mypy main/
```

### Building the Package

```bash
# Build wheel
python -m build

# Install from wheel
pip install dist/vcenter_mcp-*.whl
```

## API Endpoints

### Health Check Endpoint
- `GET /health` - Application health status (returns JSON with status information)

### MCP Protocol Endpoint
The server uses FastMCP's async `http` transport for MCP protocol communication over HTTP, compatible with Spring AI WebMVC MCP servers.

### vCenter REST API Endpoints
The server uses the vCenter REST API with the following endpoints:

- `GET /rest/vcenter/cluster` - List clusters
- `GET /rest/vcenter/resource-pool` - List resource pools
- `GET /rest/vcenter/vm` - List virtual machines

## Security Considerations

- The server operates in read-only mode
- Credentials are stored securely in environment variables or service bindings
- SSL verification is enabled by default
- No persistent storage of sensitive data
- All API requests are logged for debugging

## Troubleshooting

### Common Issues

1. **Connection failed**: Verify vCenter host URL and credentials
2. **SSL certificate errors**: Ensure vCenter has valid SSL certificates
3. **Authentication failed**: Check username and password
4. **API access denied**: Verify user has appropriate permissions
5. **MCP client timeout**: Ensure the client is configured to use `http` transport (compatible with Spring AI WebMVC)
6. **Cloud Foundry deployment issues**: Check that the app is running and accessible via HTTPS on port 443

### Logs

Check application logs for detailed error information:

```bash
# Local development
python -m main

# Cloud Foundry
cf logs vcenter-mcp-server --recent
```

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python -m main
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the MVC pattern
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

### Development Setup

```bash
# Clone and setup
git clone <your-fork-url>
cd vcenter-mcp
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black main/ tests/
```

### Adding New Features

When adding new features, follow the MVC pattern:

1. **Models**: Add new data models in `main/models/`
2. **Services**: Add API interactions in `main/services/`
3. **Controllers**: Add business logic in `main/controllers/`
4. **Views**: Add presentation logic in `main/views/`
5. **Tests**: Add corresponding tests in `tests/`

## License

[Add your license information here]

## Changelog

### 1.0.0
- Initial release
- MVC architecture implementation
- Comprehensive testing
- Cloud Foundry deployment support
- FastMCP integration
