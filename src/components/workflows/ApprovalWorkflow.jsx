import React, { useState, useEffect } from 'react';
import { API_V1_ENDPOINTS } from '../../config/api';
import { 
  CheckCircle, 
  Clock, 
  AlertCircle, 
  XCircle,
  User,
  Calendar,
  FileText,
  Play,
  Pause,
  RotateCcw,
  Eye,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  ArrowRight,
  Workflow,
  Settings
} from 'lucide-react';

const ApprovalWorkflow = ({ workflowId, onClose }) => {
  const [workflow, setWorkflow] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [approvalComment, setApprovalComment] = useState('');
  const [selectedTask, setSelectedTask] = useState(null);

  useEffect(() => {
    if (workflowId) {
      fetchWorkflowDetails();
    }
  }, [workflowId]);

  const fetchWorkflowDetails = async () => {
    try {
      setLoading(true);
      
      // Fetch workflow status and tasks
      const [statusResponse, tasksResponse] = await Promise.all([
        fetch(API_V1_ENDPOINTS.ORCHESTRATOR.WORKFLOW_STATUS(workflowId)),
        fetch(`${API_V1_ENDPOINTS.ORCHESTRATOR.WORKFLOWS}/${workflowId}/tasks`)
      ]);

      if (!statusResponse.ok || !tasksResponse.ok) {
        throw new Error('Failed to fetch workflow details');
      }

      const statusData = await statusResponse.json();
      const tasksData = await tasksResponse.json();

      setWorkflow(statusData.data);
      setTasks(tasksData.data.tasks || []);
      setError(null);
    } catch (err) {
      console.error('Error fetching workflow:', err);
      setError(err.message);
      
      // Fallback demo data
      setWorkflow({
        workflow_id: workflowId,
        campaign_id: 'camp_001',
        current_phase: 'review',
        progress: 75,
        active_tasks: 1,
        completed_tasks: 5,
        failed_tasks: 0,
        message: 'Campaign ready for review',
        start_time: '2024-01-15T10:30:00Z',
        estimated_completion: '2024-01-15T14:30:00Z'
      });
      
      setTasks([
        {
          id: `${workflowId}_discovery`,
          agent_role: 'strategist',
          phase: 'discovery',
          description: 'Analyze campaign requirements and market conditions',
          status: 'completed',
          created_at: '2024-01-15T10:30:00Z',
          completed_at: '2024-01-15T11:00:00Z',
          result: { analysis: 'Market analysis completed successfully. Target audience identified as fitness enthusiasts aged 25-45.' }
        },
        {
          id: `${workflowId}_planning`,
          agent_role: 'strategist',
          phase: 'planning',
          description: 'Develop comprehensive campaign strategy',
          status: 'completed',
          created_at: '2024-01-15T11:00:00Z',
          completed_at: '2024-01-15T11:45:00Z',
          result: { strategy: 'Multi-tier strategy developed with focus on high-intent keywords and seasonal trends.' }
        },
        {
          id: `${workflowId}_creation`,
          agent_role: 'creator',
          phase: 'creation',
          description: 'Create campaign structure, ad groups, and ads',
          status: 'completed',
          created_at: '2024-01-15T11:45:00Z',
          completed_at: '2024-01-15T13:15:00Z',
          result: { 
            structure: {
              campaign: { name: 'Fitness Equipment Q1 2024', budget: 5000 },
              ad_groups: [{ name: 'Home Gym Equipment', keywords: ['home gym', 'fitness equipment', 'workout gear'] }]
            }
          }
        },
        {
          id: `${workflowId}_review`,
          agent_role: 'analyst',
          phase: 'review',
          description: 'Review campaign for quality and compliance',
          status: 'in_progress',
          created_at: '2024-01-15T13:15:00Z',
          completed_at: null,
          dependencies: [`${workflowId}_creation`]
        },
        {
          id: `${workflowId}_launch`,
          agent_role: 'creator',
          phase: 'launch',
          description: 'Launch campaign with appropriate settings',
          status: 'pending',
          created_at: '2024-01-15T13:15:00Z',
          completed_at: null,
          dependencies: [`${workflowId}_review`]
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const approveTask = async (taskId) => {
    try {
      const response = await fetch(`${API_V1_ENDPOINTS.ORCHESTRATOR.WORKFLOWS}/${workflowId}/tasks/${taskId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment: approvalComment })
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          // Update task status locally
          setTasks(prev => prev.map(task =>
            task.id === taskId
              ? { ...task, status: 'completed', approved: true, approval_comment: approvalComment }
              : task
          ));
          
          setApprovalComment('');
          fetchWorkflowDetails(); // Refresh to get updated workflow status
          setError(null);
          return;
        }
      }
      
      throw new Error('Failed to approve task');
    } catch (err) {
      console.error('Error approving task:', err);
      setError('Failed to approve task - using demo mode');
      
      // Demo mode: Still update UI locally
      setTasks(prev => prev.map(task =>
        task.id === taskId
          ? { ...task, status: 'completed', approved: true, approval_comment: approvalComment }
          : task
      ));
      setApprovalComment('');
    }
  };

  const rejectTask = async (taskId) => {
    try {
      const response = await fetch(`${API_V1_ENDPOINTS.ORCHESTRATOR.WORKFLOWS}/${workflowId}/tasks/${taskId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ comment: approvalComment })
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          // Update task status locally
          setTasks(prev => prev.map(task =>
            task.id === taskId
              ? { ...task, status: 'failed', rejected: true, rejection_comment: approvalComment }
              : task
          ));
          
          setApprovalComment('');
          fetchWorkflowDetails();
          setError(null);
          return;
        }
      }
      
      throw new Error('Failed to reject task');
    } catch (err) {
      console.error('Error rejecting task:', err);
      setError('Failed to reject task - using demo mode');
      
      // Demo mode: Still update UI locally
      setTasks(prev => prev.map(task =>
        task.id === taskId
          ? { ...task, status: 'failed', rejected: true, rejection_comment: approvalComment }
          : task
      ));
      setApprovalComment('');
    }
  };

  const retryTask = async (taskId) => {
    try {
      const response = await fetch(`${API_V1_ENDPOINTS.ORCHESTRATOR.WORKFLOWS}/${workflowId}/tasks/${taskId}/retry`, {
        method: 'POST'
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setTasks(prev => prev.map(task =>
            task.id === taskId ? { ...task, status: 'pending' } : task
          ));
          
          fetchWorkflowDetails();
          setError(null);
          return;
        }
      }
      
      throw new Error('Failed to retry task');
    } catch (err) {
      console.error('Error retrying task:', err);
      setError('Failed to retry task - using demo mode');
      
      // Demo mode: Still update UI locally
      setTasks(prev => prev.map(task =>
        task.id === taskId ? { ...task, status: 'pending' } : task
      ));
    }
  };

  const getPhaseIcon = (phase) => {
    switch (phase) {
      case 'discovery': return Eye;
      case 'planning': return Settings;
      case 'creation': return Workflow;
      case 'review': return FileText;
      case 'launch': return Play;
      case 'monitoring': return Clock;
      default: return Clock;
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed': return CheckCircle;
      case 'in_progress': return Clock;
      case 'failed': return XCircle;
      case 'cancelled': return XCircle;
      default: return Clock;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#10b981';
      case 'in_progress': return '#f59e0b';
      case 'failed': return '#ef4444';
      case 'cancelled': return '#6b7280';
      default: return '#6b7280';
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (startTime, endTime) => {
    if (!endTime) return 'In progress...';
    const duration = new Date(endTime) - new Date(startTime);
    const minutes = Math.floor(duration / 60000);
    return `${minutes} minutes`;
  };

  if (loading) {
    return (
      <div style={{
        background: 'rgba(255, 255, 255, 0.6)',
        backdropFilter: 'blur(15px)',
        borderRadius: '20px',
        padding: '2rem',
        textAlign: 'center'
      }}>
        <Clock size={48} style={{ color: '#6366f1', animation: 'spin 1s linear infinite' }} />
        <h2 style={{ color: '#111827', marginTop: '1rem' }}>Loading Workflow...</h2>
      </div>
    );
  }

  return (
    <div style={{
      background: 'rgba(255, 255, 255, 0.6)',
      backdropFilter: 'blur(15px)',
      WebkitBackdropFilter: 'blur(15px)',
      border: '1px solid rgba(255, 255, 255, 0.5)',
      borderRadius: '20px',
      overflow: 'hidden'
    }}>
      {/* Header */}
      <div style={{
        padding: '1.5rem 2rem',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div>
          <h2 style={{
            color: '#111827',
            fontSize: '1.5rem',
            fontWeight: '700',
            margin: '0 0 0.5rem 0'
          }}>
            Campaign Approval Workflow
          </h2>
          <p style={{
            color: '#6b7280',
            fontSize: '0.875rem',
            margin: 0
          }}>
            Workflow ID: {workflowId} • Campaign: {workflow?.campaign_id}
          </p>
        </div>
        
        {onClose && (
          <button
            onClick={onClose}
            style={{
              background: 'rgba(255, 255, 255, 0.8)',
              border: '1px solid rgba(255, 255, 255, 0.5)',
              borderRadius: '8px',
              padding: '8px 12px',
              cursor: 'pointer',
              color: '#374151'
            }}
          >
            Close
          </button>
        )}
      </div>

      {/* Error Banner */}
      {error && (
        <div style={{
          background: 'rgba(239, 68, 68, 0.1)',
          borderBottom: '1px solid rgba(239, 68, 68, 0.2)',
          padding: '12px 24px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px'
        }}>
          <AlertCircle size={16} color="#dc2626" />
          <span style={{ color: '#dc2626', fontSize: '0.875rem' }}>
            {error}
          </span>
        </div>
      )}

      {/* Workflow Progress */}
      {workflow && (
        <div style={{
          padding: '1.5rem 2rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.2)'
        }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: '1rem',
            marginBottom: '1rem'
          }}>
            <div>
              <div style={{ color: '#6b7280', fontSize: '0.75rem', marginBottom: '4px' }}>
                Current Phase
              </div>
              <div style={{ color: '#111827', fontWeight: '600', textTransform: 'capitalize' }}>
                {workflow.current_phase}
              </div>
            </div>
            
            <div>
              <div style={{ color: '#6b7280', fontSize: '0.75rem', marginBottom: '4px' }}>
                Progress
              </div>
              <div style={{ color: '#111827', fontWeight: '600' }}>
                {workflow.progress.toFixed(1)}%
              </div>
            </div>
            
            <div>
              <div style={{ color: '#6b7280', fontSize: '0.75rem', marginBottom: '4px' }}>
                Completed Tasks
              </div>
              <div style={{ color: '#111827', fontWeight: '600' }}>
                {workflow.completed_tasks} / {workflow.completed_tasks + workflow.active_tasks + (tasks.length - workflow.completed_tasks - workflow.active_tasks)}
              </div>
            </div>
            
            <div>
              <div style={{ color: '#6b7280', fontSize: '0.75rem', marginBottom: '4px' }}>
                Started
              </div>
              <div style={{ color: '#111827', fontWeight: '600' }}>
                {formatDate(workflow.start_time)}
              </div>
            </div>
          </div>
          
          {/* Progress Bar */}
          <div style={{
            background: 'rgba(255, 255, 255, 0.3)',
            borderRadius: '8px',
            height: '8px',
            overflow: 'hidden'
          }}>
            <div style={{
              background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              height: '100%',
              width: `${workflow.progress}%`,
              transition: 'width 0.3s ease'
            }} />
          </div>
        </div>
      )}

      {/* Tasks List */}
      <div style={{ padding: '1rem 2rem' }}>
        <h3 style={{
          color: '#111827',
          fontSize: '1.125rem',
          fontWeight: '600',
          margin: '0 0 1rem 0'
        }}>
          Workflow Tasks
        </h3>
        
        <div style={{ display: 'grid', gap: '1rem' }}>
          {tasks.map((task, index) => {
            const PhaseIcon = getPhaseIcon(task.phase);
            const StatusIcon = getStatusIcon(task.status);
            const isSelected = selectedTask === task.id;
            const needsApproval = task.status === 'in_progress' && task.phase === 'review';
            
            return (
              <div
                key={task.id}
                style={{
                  background: isSelected 
                    ? 'rgba(99, 102, 241, 0.1)' 
                    : 'rgba(255, 255, 255, 0.4)',
                  backdropFilter: 'blur(10px)',
                  borderRadius: '12px',
                  padding: '1rem',
                  border: isSelected 
                    ? '1px solid rgba(99, 102, 241, 0.3)'
                    : '1px solid rgba(255, 255, 255, 0.3)',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
                onClick={() => setSelectedTask(isSelected ? null : task.id)}
              >
                {/* Task Header */}
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'flex-start',
                  marginBottom: '0.5rem'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <PhaseIcon size={16} color="#6366f1" />
                    <span style={{ 
                      color: '#111827', 
                      fontWeight: '600',
                      textTransform: 'capitalize'
                    }}>
                      {task.phase}
                    </span>
                    <span style={{
                      background: 'rgba(107, 114, 128, 0.1)',
                      color: '#6b7280',
                      padding: '2px 6px',
                      borderRadius: '8px',
                      fontSize: '0.75rem'
                    }}>
                      {task.agent_role}
                    </span>
                  </div>
                  
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <StatusIcon size={16} color={getStatusColor(task.status)} />
                    <span style={{
                      color: getStatusColor(task.status),
                      fontSize: '0.875rem',
                      fontWeight: '600',
                      textTransform: 'capitalize'
                    }}>
                      {task.status.replace('_', ' ')}
                    </span>
                    
                    {needsApproval && (
                      <span style={{
                        background: 'rgba(139, 92, 246, 0.2)',
                        color: '#8b5cf6',
                        padding: '2px 6px',
                        borderRadius: '8px',
                        fontSize: '0.75rem',
                        fontWeight: '600'
                      }}>
                        REVIEW REQUIRED
                      </span>
                    )}
                  </div>
                </div>
                
                <p style={{
                  color: '#6b7280',
                  fontSize: '0.875rem',
                  margin: '0 0 0.5rem 0'
                }}>
                  {task.description}
                </p>
                
                <div style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  fontSize: '0.75rem',
                  color: '#6b7280'
                }}>
                  <span>
                    Started: {formatDate(task.created_at)}
                  </span>
                  <span>
                    Duration: {formatDuration(task.created_at, task.completed_at)}
                  </span>
                </div>

                {/* Expanded Task Details */}
                {isSelected && (
                  <div style={{
                    borderTop: '1px solid rgba(255, 255, 255, 0.3)',
                    paddingTop: '1rem',
                    marginTop: '1rem'
                  }}>
                    {/* Task Result */}
                    {task.result && (
                      <div style={{ marginBottom: '1rem' }}>
                        <h4 style={{
                          color: '#111827',
                          fontSize: '0.875rem',
                          fontWeight: '600',
                          margin: '0 0 0.5rem 0'
                        }}>
                          Task Result:
                        </h4>
                        <div style={{
                          background: 'rgba(255, 255, 255, 0.5)',
                          borderRadius: '8px',
                          padding: '0.75rem',
                          fontSize: '0.875rem',
                          color: '#374151'
                        }}>
                          {typeof task.result === 'string' 
                            ? task.result 
                            : JSON.stringify(task.result, null, 2)}
                        </div>
                      </div>
                    )}

                    {/* Approval Actions */}
                    {needsApproval && (
                      <div style={{
                        background: 'rgba(139, 92, 246, 0.1)',
                        borderRadius: '8px',
                        padding: '1rem'
                      }}>
                        <h4 style={{
                          color: '#111827',
                          fontSize: '0.875rem',
                          fontWeight: '600',
                          margin: '0 0 0.75rem 0'
                        }}>
                          Approval Required
                        </h4>
                        
                        <textarea
                          value={approvalComment}
                          onChange={(e) => setApprovalComment(e.target.value)}
                          placeholder="Add approval comment (optional)..."
                          style={{
                            width: '100%',
                            minHeight: '60px',
                            padding: '0.5rem',
                            border: '1px solid rgba(255, 255, 255, 0.3)',
                            borderRadius: '6px',
                            background: 'rgba(255, 255, 255, 0.5)',
                            fontSize: '0.875rem',
                            resize: 'vertical',
                            marginBottom: '0.75rem'
                          }}
                        />
                        
                        <div style={{ display: 'flex', gap: '8px' }}>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              approveTask(task.id);
                            }}
                            style={{
                              background: 'linear-gradient(135deg, #10b981, #059669)',
                              color: 'white',
                              border: 'none',
                              borderRadius: '6px',
                              padding: '6px 12px',
                              cursor: 'pointer',
                              fontSize: '0.875rem',
                              fontWeight: '600',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px'
                            }}
                          >
                            <ThumbsUp size={14} />
                            Approve
                          </button>
                          
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              rejectTask(task.id);
                            }}
                            style={{
                              background: 'linear-gradient(135deg, #ef4444, #dc2626)',
                              color: 'white',
                              border: 'none',
                              borderRadius: '6px',
                              padding: '6px 12px',
                              cursor: 'pointer',
                              fontSize: '0.875rem',
                              fontWeight: '600',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px'
                            }}
                          >
                            <ThumbsDown size={14} />
                            Reject
                          </button>
                        </div>
                      </div>
                    )}

                    {/* Retry Option for Failed Tasks */}
                    {task.status === 'failed' && (
                      <div style={{
                        background: 'rgba(239, 68, 68, 0.1)',
                        borderRadius: '8px',
                        padding: '1rem'
                      }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <div>
                            <h4 style={{
                              color: '#dc2626',
                              fontSize: '0.875rem',
                              fontWeight: '600',
                              margin: '0 0 0.25rem 0'
                            }}>
                              Task Failed
                            </h4>
                            {task.error && (
                              <p style={{
                                color: '#dc2626',
                                fontSize: '0.75rem',
                                margin: 0
                              }}>
                                {task.error}
                              </p>
                            )}
                          </div>
                          
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              retryTask(task.id);
                            }}
                            style={{
                              background: 'linear-gradient(135deg, #f59e0b, #d97706)',
                              color: 'white',
                              border: 'none',
                              borderRadius: '6px',
                              padding: '6px 12px',
                              cursor: 'pointer',
                              fontSize: '0.875rem',
                              fontWeight: '600',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '4px'
                            }}
                          >
                            <RotateCcw size={14} />
                            Retry
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default ApprovalWorkflow;