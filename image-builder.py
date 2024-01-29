#!/usr/bin/env python3

import argparse
import json
import sys
from docker_manager.docker_config import DockerConfig
from docker_manager.docker_container_manager import DockerContainerManager
from docker_manager.docker_dependency_checker import DockerDependencyChecker
from docker_manager.docker_image_builder import DockerImageBuilder
from test_docker_manager.docker_test_suite import DockerTestSuite

# Define exit status constants
EXIT_SUCCESS = 0
EXIT_FAIL = 1

def init_parser():
    _description="Arbitrage-Bot Docker Management Script"
    parser = argparse.ArgumentParser(description=_description)
    parser.add_argument("-c", "--config", required=True, help="Path to the configuration file")
    parser.add_argument("-v", "--verbose", action='store_true', help="Enable output")
    parser.add_argument("-l", "--logging", action='store_true', help="Enable logging")
    parser.add_argument("--build-image", action='store_true', help="Build Docker image")
    parser.add_argument("--create-container", action='store_true', help="Create Docker container")
    parser.add_argument('--run-tests', action='store_true', help='Run unit tests')
    return parser

def main():
    parser = init_parser()
    args = parser.parse_args()

    try: # to open the config file
        with open(args.config, 'r') as config_file:
            config_json = json.load(config_file)
    except Exception as e:
        print(f"Error reading config file: {e}")
        sys.exit(EXIT_FAIL)

    config_json['verbose'] = args.verbose
    config_json['logging'] = args.logging

    try:
        # init the module
        docker_config = DockerConfig(config_dict=config_json)
        dependency_checker = DockerDependencyChecker(docker_config)
        dependency_checker.prepare_environment()

        image_name_tag = None
        if args.build_image or args.create_container:
            image_builder = DockerImageBuilder(docker_config)
            image_name_tag = image_builder.build_image()

            if image_name_tag is not None:
                print("Docker image built successfully.")

        if args.create_container:
            if image_name_tag is not None:
                container_manager = DockerContainerManager(docker_config)
                container_manager.create_container(image_name_tag)
                print("Docker container created successfully.")
            else:
                print("Error: Docker image needs to be built before creating a container.")
                sys.exit(EXIT_FAIL)

        if args.run_tests:
            test_suite = DockerTestSuite()
            test_suite.run()

    except Exception as e:
        print(f"Error during Docker operations: {e}")
        sys.exit(EXIT_FAIL)

    print("Docker build and create script completed successfully.")
    sys.exit(EXIT_SUCCESS)


if __name__ == '__main__':
    main()