/**
 * API Proxy for FastAPI Integration
 *
 * This route proxies requests from the Next.js frontend to the FastAPI backend,
 * allowing us to preserve the Python analytics capabilities.
 */

import { NextRequest, NextResponse } from 'next/server';

// Get the FastAPI URL from environment variables
const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:8000';

/**
 * Main handler for all API routes
 * Uses dynamic route segments to match any path and forwards to the FastAPI backend
 */
export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const url = new URL(request.url);
  const fullApiPath = `${PYTHON_API_URL}/${path}${url.search}`;

  try {
    const response = await fetch(fullApiPath, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // Forward authorization header if present
        ...(request.headers.get('authorization') 
          ? { 'Authorization': request.headers.get('authorization') as string } 
          : {})
      },
    });

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
      headers: {
        'Cache-Control': 'no-store, max-age=0',
      },
    });
  } catch (error) {
    console.error(`Error proxying to ${fullApiPath}:`, error);
    return NextResponse.json(
      { error: 'Failed to fetch data from Python API' },
      { status: 500 }
    );
  }
}

/**
 * POST handler for API routes
 */
export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const fullApiPath = `${PYTHON_API_URL}/${path}`;
  
  try {
    const body = await request.json();
    const response = await fetch(fullApiPath, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Forward authorization header if present
        ...(request.headers.get('authorization') 
          ? { 'Authorization': request.headers.get('authorization') as string } 
          : {})
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
      headers: {
        'Cache-Control': 'no-store, max-age=0',
      },
    });
  } catch (error) {
    console.error(`Error proxying to ${fullApiPath}:`, error);
    return NextResponse.json(
      { error: 'Failed to send data to Python API' },
      { status: 500 }
    );
  }
}

/**
 * PUT handler for API routes
 */
export async function PUT(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const fullApiPath = `${PYTHON_API_URL}/${path}`;
  
  try {
    const body = await request.json();
    const response = await fetch(fullApiPath, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        // Forward authorization header if present
        ...(request.headers.get('authorization') 
          ? { 'Authorization': request.headers.get('authorization') as string } 
          : {})
      },
      body: JSON.stringify(body),
    });

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
      headers: {
        'Cache-Control': 'no-store, max-age=0',
      },
    });
  } catch (error) {
    console.error(`Error proxying to ${fullApiPath}:`, error);
    return NextResponse.json(
      { error: 'Failed to update data in Python API' },
      { status: 500 }
    );
  }
}

/**
 * DELETE handler for API routes
 */
export async function DELETE(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  const path = params.path.join('/');
  const url = new URL(request.url);
  const fullApiPath = `${PYTHON_API_URL}/${path}${url.search}`;
  
  try {
    const response = await fetch(fullApiPath, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        // Forward authorization header if present
        ...(request.headers.get('authorization') 
          ? { 'Authorization': request.headers.get('authorization') as string } 
          : {})
      },
    });

    // Some DELETE endpoints return no content
    if (response.status === 204) {
      return new NextResponse(null, { status: 204 });
    }

    const data = await response.json();

    return NextResponse.json(data, {
      status: response.status,
      headers: {
        'Cache-Control': 'no-store, max-age=0',
      },
    });
  } catch (error) {
    console.error(`Error proxying to ${fullApiPath}:`, error);
    return NextResponse.json(
      { error: 'Failed to delete data in Python API' },
      { status: 500 }
    );
  }
}