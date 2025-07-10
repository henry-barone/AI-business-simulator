// Business Simulation State Management
// Handles persistence of questionnaire data and simulation results across page navigation

export interface CompanyData {
  id: string;
  name: string;
  email: string;
  emailConsent: boolean;
}

export interface SimulationData {
  simulation_id?: number;
  [key: string]: any;
}

export interface QuestionnaireData {
  answers: Record<string, string>;
  completedAt?: string;
  questionCount: number;
}

export interface BusinessSimulationState {
  companyData: CompanyData | null;
  simulationData: SimulationData | null;
  questionnaireData: QuestionnaireData | null;
  fullReportData: any;
  lastUpdated: string;
}

class BusinessSimulationStateManager {
  private readonly STORAGE_KEY = 'business_simulation_state';
  private readonly STORAGE_EXPIRY_HOURS = 24; // 24 hours expiry
  private listeners: Set<() => void> = new Set();

  // Save complete state to localStorage
  saveState(state: Partial<BusinessSimulationState>): void {
    try {
      const currentState = this.getState();
      const newState: BusinessSimulationState = {
        ...currentState,
        ...state,
        lastUpdated: new Date().toISOString()
      };
      
      localStorage.setItem(this.STORAGE_KEY, JSON.stringify(newState));
      
      // Notify all listeners about the state change
      this.listeners.forEach(listener => listener());
    } catch (error) {
      console.warn('Failed to save business simulation state:', error);
    }
  }

  // Get complete state from localStorage
  getState(): BusinessSimulationState {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      if (!stored) {
        return this.getEmptyState();
      }

      const state: BusinessSimulationState = JSON.parse(stored);
      
      // Check if state has expired
      if (this.isStateExpired(state.lastUpdated)) {
        this.clearState();
        return this.getEmptyState();
      }

      return state;
    } catch (error) {
      console.warn('Failed to retrieve business simulation state:', error);
      return this.getEmptyState();
    }
  }

  // Update questionnaire data incrementally
  updateQuestionnaireData(answers: Record<string, string>, questionCount: number): void {
    const currentState = this.getState();
    const questionnaireData: QuestionnaireData = {
      answers,
      questionCount,
      completedAt: questionCount >= 12 ? new Date().toISOString() : undefined
    };

    this.saveState({
      questionnaireData
    });
  }

  // Update simulation data
  updateSimulationData(simulationData: SimulationData): void {
    this.saveState({
      simulationData
    });
  }

  // Update company data
  updateCompanyData(companyData: CompanyData): void {
    this.saveState({
      companyData
    });
  }

  // Update full report data
  updateFullReportData(fullReportData: any): void {
    this.saveState({
      fullReportData
    });
  }

  // Check if questionnaire is completed
  isQuestionnaireCompleted(): boolean {
    const state = this.getState();
    return state.questionnaireData?.completedAt !== undefined;
  }

  // Check if simulation data exists
  hasSimulationData(): boolean {
    const state = this.getState();
    return state.simulationData !== null && state.simulationData !== undefined;
  }

  // Clear questionnaire data (for re-answering)
  clearQuestionnaireData(): void {
    const currentState = this.getState();
    this.saveState({
      questionnaireData: null,
      simulationData: null, // Clear simulation when questionnaire is reset
      fullReportData: null
    });
  }

  // Clear all state
  clearState(): void {
    try {
      localStorage.removeItem(this.STORAGE_KEY);
    } catch (error) {
      console.warn('Failed to clear business simulation state:', error);
    }
  }

  // Check if company exists and has completed questionnaire
  hasCompletedAssessment(): boolean {
    const state = this.getState();
    return state.companyData !== null && this.isQuestionnaireCompleted();
  }

  // Get the current step based on state
  getCurrentStep(): 'landing' | 'setup' | 'upload' | 'questionnaire' | 'processing' | 'results' {
    const state = this.getState();
    
    if (!state.companyData) {
      return 'landing';
    }
    
    if (!state.questionnaireData || Object.keys(state.questionnaireData.answers).length === 0) {
      return 'upload'; // Skip setup since company exists, go to upload
    }
    
    if (!this.isQuestionnaireCompleted()) {
      return 'questionnaire';
    }
    
    if (this.hasSimulationData()) {
      return 'results';
    }
    
    return 'processing';
  }

  private getEmptyState(): BusinessSimulationState {
    return {
      companyData: null,
      simulationData: null,
      questionnaireData: null,
      fullReportData: null,
      lastUpdated: new Date().toISOString()
    };
  }

  private isStateExpired(lastUpdated: string): boolean {
    try {
      const lastUpdateTime = new Date(lastUpdated).getTime();
      const expiryTime = this.STORAGE_EXPIRY_HOURS * 60 * 60 * 1000; // Convert hours to milliseconds
      return Date.now() - lastUpdateTime > expiryTime;
    } catch {
      return true; // If we can't parse the date, consider it expired
    }
  }

  // Add listener for state changes
  addListener(listener: () => void): () => void {
    this.listeners.add(listener);
    
    // Return cleanup function
    return () => {
      this.listeners.delete(listener);
    };
  }

  // Remove listener
  removeListener(listener: () => void): void {
    this.listeners.delete(listener);
  }
}

// Export singleton instance
export const businessSimulationState = new BusinessSimulationStateManager();