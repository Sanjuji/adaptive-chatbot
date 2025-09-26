#!/usr/bin/env python3
"""
Simple working chatbot
"""

import argparse

def main():
    parser = argparse.ArgumentParser(description="Simple Chatbot")
    parser.add_argument("--mode", choices=["menu", "text"], default="menu")
    args = parser.parse_args()
    print(f"Chatbot running in {args.mode} mode")

if __name__ == "__main__":
    main()
