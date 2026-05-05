"""Entry point for python -m brain.cli"""
from brain.cli import main
import sys
sys.exit(main() or 0)
