#!/usr/bin/env python
"""
Tests for BlackDuck MCP Server

Tests the Model Context Protocol server functionality using FastMCP's
in-memory testing patterns.
"""

import pytest
import os
from unittest.mock import patch, MagicMock

# Skip all tests if FastMCP is not installed
pytest.importorskip("fastmcp")

from blackduck.mcp_server import BlackDuckMCPServer


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for MCP server"""
    monkeypatch.setenv('BLACKDUCK_URL', 'https://test.blackduck.url')
    monkeypatch.setenv('BLACKDUCK_TOKEN', 'test-token-12345')


@pytest.fixture
def mock_blackduck_client():
    """Create a mock BlackDuck client for testing"""
    mock_client = MagicMock()

    # Mock project data
    mock_projects = [
        {
            'name': 'test-project-1',
            'description': 'Test project 1 description',
            'projectOwner': 'test-user',
            'createdAt': '2024-01-01T00:00:00Z',
            'updatedAt': '2024-01-02T00:00:00Z',
            '_meta': {
                'href': 'https://test.blackduck.url/api/projects/proj-1'
            }
        },
        {
            'name': 'test-project-2',
            'description': 'Test project 2 description',
            'projectOwner': 'test-user',
            'createdAt': '2024-01-03T00:00:00Z',
            'updatedAt': '2024-01-04T00:00:00Z',
            '_meta': {
                'href': 'https://test.blackduck.url/api/projects/proj-2'
            }
        }
    ]

    # Mock version data
    mock_versions = [
        {
            'versionName': '1.0.0',
            'nickname': 'v1',
            'phase': 'DEVELOPMENT',
            'distribution': 'INTERNAL',
            'createdAt': '2024-01-01T00:00:00Z',
            'settingUpdatedAt': '2024-01-02T00:00:00Z',
            '_meta': {
                'href': 'https://test.blackduck.url/api/versions/ver-1'
            }
        }
    ]

    # Mock vulnerability data
    mock_vulnerabilities = [
        {
            'componentName': 'test-component',
            'componentVersionName': '1.0.0',
            'vulnerabilityName': 'CVE-2024-0001',
            'severity': 'HIGH',
            'baseScore': 7.5,
            'overallScore': 7.5,
            'remediationStatus': 'NEW',
            'description': 'Test vulnerability',
            'publishedDate': '2024-01-01T00:00:00Z',
            'updatedDate': '2024-01-02T00:00:00Z'
        }
    ]

    # Mock component data
    mock_components = [
        {
            'componentName': 'test-component',
            'componentVersionName': '1.0.0',
            'matchTypes': ['FILE'],
            'usages': ['DYNAMICALLY_LINKED'],
            'licenses': [{'licenseDisplay': 'MIT'}],
            'policyStatus': 'IN_VIOLATION',
            'securityRiskProfile': {'HIGH': 1},
            'activityData': {'trending': 'STABLE'}
        }
    ]

    # Set up mock return values
    mock_client.get_resource.return_value = iter(mock_projects)

    return mock_client, mock_projects, mock_versions, mock_vulnerabilities, mock_components


@pytest.fixture
def mcp_server(mock_env_vars, mock_blackduck_client):
    """Create MCP server with mocked BlackDuck client"""
    mock_client, projects, versions, vulns, components = mock_blackduck_client

    with patch('blackduck.mcp_server.Client', return_value=mock_client):
        server = BlackDuckMCPServer()
        # Store mock data for test assertions
        server._test_projects = projects
        server._test_versions = versions
        server._test_vulnerabilities = vulns
        server._test_components = components
        yield server


class TestMCPServerInitialization:
    """Test MCP server initialization"""

    def test_server_requires_env_vars(self):
        """Test that server raises error without environment variables"""
        with pytest.raises(ValueError, match="Missing required environment variables"):
            BlackDuckMCPServer()

    def test_server_initializes_with_env_vars(self, mock_env_vars, mock_blackduck_client):
        """Test that server initializes correctly with environment variables"""
        mock_client, *_ = mock_blackduck_client

        with patch('blackduck.mcp_server.Client', return_value=mock_client) as mock_client_class:
            server = BlackDuckMCPServer()

            # Verify Client was initialized with correct parameters
            mock_client_class.assert_called_once_with(
                base_url='https://test.blackduck.url',
                token='test-token-12345',
                verify=True,
                timeout=30.0,
                retries=3
            )

            assert server.client is not None
            assert server.mcp is not None


class TestListProjects:
    """Test list_projects MCP tool"""

    def test_list_projects_default_limit(self, mcp_server):
        """Test listing projects with default limit"""
        # Call the tool directly through the server's registered tools
        result = None
        for tool in mcp_server.mcp._tools:
            if tool.__name__ == 'list_projects':
                result = tool()
                break

        assert result is not None
        assert len(result) == 2
        assert result[0]['name'] == 'test-project-1'
        assert result[1]['name'] == 'test-project-2'

    def test_list_projects_with_limit(self, mcp_server):
        """Test listing projects with custom limit"""
        result = None
        for tool in mcp_server.mcp._tools:
            if tool.__name__ == 'list_projects':
                result = tool(limit=1)
                break

        assert result is not None
        assert len(result) == 1
        assert result[0]['name'] == 'test-project-1'


class TestGetProjectDetails:
    """Test get_project_details MCP tool"""

    def test_get_project_details_exact_match(self, mcp_server):
        """Test getting project details with exact name match"""
        # Mock the search to return our test project
        mcp_server.client.get_resource.return_value = iter(mcp_server._test_projects)

        result = None
        for tool in mcp_server.mcp._tools:
            if tool.__name__ == 'get_project_details':
                result = tool(project_name='test-project-1')
                break

        assert result is not None
        assert result['name'] == 'test-project-1'
        assert result['description'] == 'Test project 1 description'

    def test_get_project_details_case_insensitive(self, mcp_server):
        """Test getting project details with case-insensitive search"""
        mcp_server.client.get_resource.return_value = iter(mcp_server._test_projects)

        result = None
        for tool in mcp_server.mcp._tools:
            if tool.__name__ == 'get_project_details':
                result = tool(project_name='TEST-PROJECT-1')
                break

        assert result is not None
        assert result['name'] == 'test-project-1'

    def test_get_project_details_not_found(self, mcp_server):
        """Test getting project details for non-existent project"""
        mcp_server.client.get_resource.return_value = iter(mcp_server._test_projects)

        result = None
        for tool in mcp_server.mcp._tools:
            if tool.__name__ == 'get_project_details':
                result = tool(project_name='non-existent-project')
                break

        assert result is None


class TestListProjectVersions:
    """Test list_project_versions MCP tool"""

    def test_list_project_versions(self, mcp_server):
        """Test listing project versions"""
        # Set up mock to return project, then versions
        mcp_server.client.get_resource.side_effect = [
            iter(mcp_server._test_projects),  # First call: search for project
            iter(mcp_server._test_versions)   # Second call: get versions
        ]

        result = None
        for tool in mcp_server.mcp._tools:
            if tool.__name__ == 'list_project_versions':
                result = tool(project_name='test-project-1')
                break

        assert result is not None
        assert len(result) == 1
        assert result[0]['versionName'] == '1.0.0'
        assert result[0]['phase'] == 'DEVELOPMENT'

    def test_list_project_versions_project_not_found(self, mcp_server):
        """Test listing versions for non-existent project"""
        mcp_server.client.get_resource.return_value = iter([])

        result = None
        for tool in mcp_server.mcp._tools:
            if tool.__name__ == 'list_project_versions':
                result = tool(project_name='non-existent-project')
                break

        assert result == []


class TestSearchProjects:
    """Test search_projects MCP tool"""

    def test_search_projects_by_name(self, mcp_server):
        """Test searching projects by name"""
        mcp_server.client.get_resource.return_value = iter(mcp_server._test_projects)

        result = None
        for tool in mcp_server.mcp._tools:
            if tool.__name__ == 'search_projects':
                result = tool(query='test-project')
                break

        assert result is not None
        assert len(result) == 2
        # Results should be sorted by relevance
        assert all('relevance' in r for r in result)

    def test_search_projects_relevance_scoring(self, mcp_server):
        """Test that search results are sorted by relevance"""
        mcp_server.client.get_resource.return_value = iter(mcp_server._test_projects)

        result = None
        for tool in mcp_server.mcp._tools:
            if tool.__name__ == 'search_projects':
                result = tool(query='project-1')
                break

        assert result is not None
        # First result should have higher relevance (exact match in name)
        assert result[0]['name'] == 'test-project-1'
        assert result[0]['relevance'] >= result[1]['relevance']


class TestGetProjectVulnerabilities:
    """Test get_project_vulnerabilities MCP tool"""

    def test_get_vulnerabilities_latest_version(self, mcp_server):
        """Test getting vulnerabilities for latest version"""
        mcp_server.client.get_resource.side_effect = [
            iter(mcp_server._test_projects),         # Search for project
            iter(mcp_server._test_versions),         # Get versions
            iter(mcp_server._test_vulnerabilities)   # Get vulnerabilities
        ]

        result = None
        for tool in mcp_server.mcp._tools:
            if tool.__name__ == 'get_project_vulnerabilities':
                result = tool(project_name='test-project-1')
                break

        assert result is not None
        assert len(result) == 1
        assert result[0]['vulnerabilityName'] == 'CVE-2024-0001'
        assert result[0]['severity'] == 'HIGH'

    def test_get_vulnerabilities_specific_version(self, mcp_server):
        """Test getting vulnerabilities for specific version"""
        mcp_server.client.get_resource.side_effect = [
            iter(mcp_server._test_projects),
            iter(mcp_server._test_versions),
            iter(mcp_server._test_vulnerabilities)
        ]

        result = None
        for tool in mcp_server.mcp._tools:
            if tool.__name__ == 'get_project_vulnerabilities':
                result = tool(project_name='test-project-1', version_name='1.0.0')
                break

        assert result is not None
        assert len(result) == 1


class TestListProjectComponents:
    """Test list_project_components MCP tool"""

    def test_list_components_latest_version(self, mcp_server):
        """Test listing components for latest version"""
        mcp_server.client.get_resource.side_effect = [
            iter(mcp_server._test_projects),     # Search for project
            iter(mcp_server._test_versions),     # Get versions
            iter(mcp_server._test_components)    # Get components
        ]

        result = None
        for tool in mcp_server.mcp._tools:
            if tool.__name__ == 'list_project_components':
                result = tool(project_name='test-project-1')
                break

        assert result is not None
        assert len(result) == 1
        assert result[0]['componentName'] == 'test-component'
        assert result[0]['licenseDisplay'] == 'MIT'

    def test_list_components_no_license(self, mcp_server):
        """Test listing components with no license information"""
        # Create component without license
        component_no_license = {
            'componentName': 'unlicensed-component',
            'componentVersionName': '1.0.0',
            'matchTypes': ['FILE'],
            'usages': ['DYNAMICALLY_LINKED'],
            'licenses': [],
            'policyStatus': 'NOT_IN_VIOLATION',
            'securityRiskProfile': {},
            'activityData': {}
        }

        mcp_server.client.get_resource.side_effect = [
            iter(mcp_server._test_projects),
            iter(mcp_server._test_versions),
            iter([component_no_license])
        ]

        result = None
        for tool in mcp_server.mcp._tools:
            if tool.__name__ == 'list_project_components':
                result = tool(project_name='test-project-1')
                break

        assert result is not None
        assert len(result) == 1
        assert result[0]['licenseDisplay'] == 'Unknown'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
