"""
Command-line interface for DocusaurusGenerator.
"""
import os
import sys
import logging
import argparse
from typing import Optional, Dict, Any


def setup_logging(verbose: bool = False) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        verbose: Whether to enable verbose logging
        
    Returns:
        Logger instance
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    return logging.getLogger('docusaurus_generator')


def generate_content(prompt: str, model: str) -> Optional[str]:
    model_provider, model_name = model.split('/')
    
    if model_provider == "openai":
        collected_response = []
        for token in generate_with_openai(prompt, model_name):
            if token is not None:
                #print(token, end='', flush=True)
                collected_response.append(token)
            else:
                print("\nError occurred during generation.")
        print()  # Print a newline at the end
        return ''.join(collected_response)
    elif model_provider == "azure":
        #collected_response = []
        #for token in generate_with_azure(prompt, model_name):
        #    if token is not None:
        #        print(token, end='', flush=True)
        #        collected_response.append(token)
        #    else:
        #        print("\nError occurred during generation.")
        #print()  # Print a newline at the end
        return generate_with_azure(prompt, model_name)
    elif model_provider == "ollama":
        return generate_with_ollama(prompt, model_name)
    else:
        logging.error(f"Unsupported model provider: {model_provider}")
        return None


def generate_with_azure(prompt: str, model_name: str) -> Optional[str]:
    from azure.identity import ClientSecretCredential, get_bearer_token_provider
    from openai import AzureOpenAI
    from dotenv import load_dotenv
    import numpy as np
    
    try:
        load_dotenv()

        APIM_SUBSCRIPTION_KEY = os.getenv("APIM_SUBSCRIPTION_KEY")
        default_headers = {}
        if APIM_SUBSCRIPTION_KEY != None:
            # only set this if the APIM API requires a subscription...
            default_headers["Ocp-Apim-Subscription-Key"] = APIM_SUBSCRIPTION_KEY 

        # Set up authority and credentials for Azure authentication
        credential = ClientSecretCredential(
            tenant_id=os.getenv("AZURE_TENANT_ID"),
            client_id=os.getenv("AZURE_CLIENT_ID"),
            client_secret=os.getenv("AZURE_CLIENT_SECRET"),
            authority="https://login.microsoftonline.com",
        )

        token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")

        client = AzureOpenAI(
            # azure_ad_token=access_token.token,
            azure_ad_token_provider=token_provider,
            api_version=os.getenv("API_VERSION"),
            azure_endpoint=os.getenv("API_ENDPOINT"),
            default_headers=default_headers,
        )

        completion = client.chat.completions.create(
            messages = [
                {
                    "role": "system",
                    "content": "As a SLIM Best Practice User, your role is to understand, apply, and implement the best practices for Software Lifecycle Improvement and Modernization (SLIM) within your software projects. You should aim to optimize your software development processes, enhance the quality of your software products, and ensure continuous improvement across all stages of the software lifecycle.",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model_name
        )
        return completion.choices[0].message.content
    except Exception as e:
        print(f"An error occurred running on Azure model: {str(e)}")
        return None


def generate_with_openai(prompt: str, model_name: str) -> Optional[str]:
    from openai import OpenAI
    from dotenv import load_dotenv
    load_dotenv()
    try:    
        client = OpenAI(api_key = os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    except Exception as e:
        print(f"An error occurred running OpenAI model: {e}")
        yield None

def generate_with_ollama(prompt: str, model_name: str) -> Optional[str]:
    import ollama

    try:
        response = ollama.chat(model=model_name, messages=[
        {
            'role': 'user',
            'content': prompt,
        },
        ])
        #print(response['message']['content'])
        return (response['message']['content'])
    except Exception as e:
        logging.error(f"Error running Ollama model: {e}")
        return None

    #try:
    #    response = subprocess.run(['ollama', 'run', model_name, prompt], capture_output=True, text=True, check=True)
    #    return response.stdout.strip()
    #except subprocess.CalledProcessError as e:
    #    logging.error(f"Error running Ollama model: {e}")
    #    return None


def parse_arguments() -> Dict[str, Any]:
    """
    Parse command-line arguments.
    
    Returns:
        Dictionary of parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Generate Docusaurus documentation from repository content'
    )
    
    parser.add_argument(
        'repo_path',
        help='Path to the repository'
    )
    
    parser.add_argument(
        '--output-dir',
        '-o',
        help='Directory where documentation should be generated',
        default='./docusaurus'
    )
    
    parser.add_argument(
        '--config',
        '-c',
        help='Path to configuration file'
    )
    
    parser.add_argument(
        '--use-ai',
        help='Enable AI enhancement with specified model (e.g., "openai/gpt-4o")'
    )
    
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--install',
        action='store_true',
        help='Install Docusaurus dependencies'
    )
    
    parser.add_argument(
        '--start',
        action='store_true',
        help='Start Docusaurus development server after generation'
    )
    
    return vars(parser.parse_args())


def main() -> int:
    """
    Main entry point for the command-line interface.
    
    Returns:
        Exit code
    """
    # Parse arguments
    args = parse_arguments()
    
    # Set up logging
    logger = setup_logging(args['verbose'])
    
    # Load configuration if provided
    config = {}
    if args['config']:
        import yaml
        try:
            with open(args['config'], 'r') as f:
                config = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return 1
    
    # Import DocusaurusGenerator locally to avoid circular imports
    from .generator import DocusaurusGenerator
    
    # Create generator
    generator = DocusaurusGenerator(
        repo_path=args['repo_path'],
        output_dir=args['output_dir'],
        config=config,
        use_ai=args['use_ai']
    )
    
    # Generate documentation and optionally install and start
    success = generator.setup_and_start(
        install=args['install'],
        start=args['start']
    )
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())