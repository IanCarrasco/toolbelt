#!/usr/bin/env python3
"""
Test script to verify the API works without coroutine errors
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_toolbelt_session():
    """Test the ToolbeltSession class"""
    try:
        from lib.toolbelt import ToolbeltSession
        from openai import OpenAI
        
        # Create a mock client (you'll need to set OPENAI_TOOLBELT_KEY)
        client = OpenAI(api_key=os.environ.get('OPENAI_TOOLBELT_KEY', 'test-key'))
        session = ToolbeltSession(client=client)
        
        print("✓ ToolbeltSession imported successfully")
        
        # Test that the run method is an async generator
        async_gen = session.run("test query")
        print("✓ session.run() returns an async generator")
        
        # Test yielding a few messages
        count = 0
        async for message in async_gen:
            print(f"✓ Received message: {message}")
            count += 1
            if count >= 3:  # Just test first few messages
                break
                
        print("✓ ToolbeltSession.run() works correctly")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def test_api_endpoint():
    """Test the API endpoint"""
    try:
        from api.api import run_toolbelt_session
        from api.models.session_request import SessionRequest
        
        print("✓ API modules imported successfully")
        
        # Test the async generator function
        request = SessionRequest(user_query="test query")
        async_gen = run_toolbelt_session(request)
        
        print("✓ run_toolbelt_session() returns an async generator")
        
        # Test yielding a few messages
        count = 0
        async for message in async_gen:
            print(f"✓ API yielded: {message}")
            count += 1
            if count >= 3:  # Just test first few messages
                break
                
        print("✓ API endpoint works correctly")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

async def main():
    """Run all tests"""
    print("Testing ToolbeltSession...")
    session_ok = await test_toolbelt_session()
    
    print("\nTesting API endpoint...")
    api_ok = await test_api_endpoint()
    
    if session_ok and api_ok:
        print("\n🎉 All tests passed! The coroutine error should be fixed.")
    else:
        print("\n❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
