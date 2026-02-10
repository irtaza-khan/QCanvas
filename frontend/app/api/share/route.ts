import { NextRequest, NextResponse } from 'next/server';

interface ShareFileRequest {
    id: string;
    title: string;
    description: string;
    framework: string;
    difficulty: string;
    category: string;
    tags: string;
    code: string;
    filename: string;
}

// In-memory storage for shared files (mock database)
const mockSharedFiles: ShareFileRequest[] = [];

export async function POST(request: NextRequest) {
    try {
        const body: ShareFileRequest = await request.json();

        // Validate required fields
        if (!body.id || !body.title || !body.code) {
            return NextResponse.json(
                { error: 'Missing required fields (ID, Title, Code)' },
                { status: 400 }
            );
        }

        // Check if ID already exists
        if (mockSharedFiles.some(file => file.id === body.id)) {
            return NextResponse.json(
                { error: 'File with this ID already exists. Please choose a different ID.' },
                { status: 409 }
            );
        }

        // Store the file
        mockSharedFiles.push(body);

        // Initial mock data log
        console.log('File shared:', body);

        return NextResponse.json({
            success: true,
            message: 'File shared successfully',
            id: body.id
        });
    } catch (error) {
        console.error('Share error:', error);
        return NextResponse.json(
            { error: 'Failed to share file' },
            { status: 500 }
        );
    }
}

export async function GET() {
    return NextResponse.json({
        files: mockSharedFiles,
        count: mockSharedFiles.length
    });
}
