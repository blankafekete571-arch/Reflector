import './ProgressBar.css';

function ProgressBar({ currentStep, stepTitle, totalSteps }) {
  const percentage = (currentStep / totalSteps) * 100;

  return (
    <div className="progress-container">
      <div className="progress-info">
        <span className="progress-text">Step {currentStep} of {totalSteps}</span>
        <span className="step-title">{stepTitle}</span>
      </div>
      <div className="progress-bar">
        <div 
          className="progress-fill" 
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
}

export default ProgressBar;
