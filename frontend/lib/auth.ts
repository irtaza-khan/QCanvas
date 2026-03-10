import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from './authStore';

export function useRequireAuth(redirectUrl = '/login') {
    const { isAuthenticated, isLoading } = useAuthStore();
    const router = useRouter();

    useEffect(() => {
        if (!isLoading && !isAuthenticated) {
            router.push(redirectUrl as Parameters<typeof router.push>[0]);
        }
    }, [isAuthenticated, isLoading, router, redirectUrl]);

    return { isAuthenticated, loading: isLoading };
}
