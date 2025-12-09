import { useState, useEffect } from 'react';
import { healthCheck } from './api';

export interface Features {
    hybrid_execution: boolean;
    project_management: boolean;
    advanced_monitoring: boolean;
    circuit_visualization: boolean;
}

export const useFeatures = () => {
    const [features, setFeatures] = useState<Features>({
        hybrid_execution: false,
        project_management: false,
        advanced_monitoring: false,
        circuit_visualization: false,
    });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchFeatures = async () => {
            try {
                const response = await healthCheck();
                if (response.success && response.data?.features) {
                    // Type assertion to match Features interface
                    setFeatures(response.data.features as unknown as Features);
                }
            } catch (error) {
                console.error('Failed to fetch feature flags:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchFeatures();
    }, []);

    return { features, loading };
};
