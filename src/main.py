"""
Main entry point for the AI Call Secretary application.
"""
import os
import sys
import logging
import argparse
import uvicorn
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="AI Call Secretary")
    
    parser.add_argument(
        "--config",
        type=str,
        default=os.environ.get("CONFIG_PATH", "config/default.yml"),
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--mode",
        type=str,
        choices=["api", "telephony", "all"],
        default="all",
        help="Run mode (api, telephony, or all)"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("HOST", "0.0.0.0"),
        help="Host to bind to"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("PORT", 8080)),
        help="Port to bind to"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    return parser.parse_args()


def run_api(args):
    """Run the API server."""
    from src.api import api_app
    
    # Set config path as environment variable
    os.environ["CONFIG_PATH"] = args.config
    
    # Configure logging level
    log_level = "debug" if args.debug else "info"
    
    # Start API server
    logger.info(f"Starting API server on {args.host}:{args.port}")
    uvicorn.run(
        "src.api.routes:app",
        host=args.host,
        port=args.port,
        reload=args.debug,
        log_level=log_level
    )


def run_telephony(args):
    """Run the telephony server."""
    from src.telephony.call_handler import CallHandler
    
    # Set config path as environment variable
    os.environ["CONFIG_PATH"] = args.config
    
    # Create call handler
    call_handler = CallHandler(config_path=args.config)
    
    # Start telephony server
    logger.info("Starting telephony server")
    call_handler.start()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Set config path as environment variable
    os.environ["CONFIG_PATH"] = args.config
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        if args.mode == "api":
            run_api(args)
        elif args.mode == "telephony":
            run_telephony(args)
        else:  # "all"
            # In production, you'd use a process manager like supervisord or systemd
            # to run both services. For development, we'll use concurrent.futures.
            import concurrent.futures
            with concurrent.futures.ProcessPoolExecutor(max_workers=2) as executor:
                executor.submit(run_api, args)
                executor.submit(run_telephony, args)
                
                # Wait for futures to complete
                concurrent.futures.wait(executor._pending_work_items)
    except KeyboardInterrupt:
        logger.info("Shutting down AI Call Secretary")
    except Exception as e:
        logger.error(f"Error running AI Call Secretary: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()