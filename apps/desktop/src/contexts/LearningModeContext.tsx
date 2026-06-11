import { createContext, useContext, useState, type ReactNode } from "react";

interface LearningModeContextType {
  learningMode: boolean;
  setLearningMode: (v: boolean) => void;
}

const LearningModeContext = createContext<LearningModeContextType>({
  learningMode: false,
  setLearningMode: () => {},
});

export function LearningModeProvider({ children }: { children: ReactNode }) {
  const [learningMode, setLearningMode] = useState(false);
  return (
    <LearningModeContext.Provider value={{ learningMode, setLearningMode }}>
      {children}
    </LearningModeContext.Provider>
  );
}

export function useLearningMode() {
  return useContext(LearningModeContext);
}
