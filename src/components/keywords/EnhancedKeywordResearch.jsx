import React, { useState, useEffect } from 'react';
import { 
  Search, 
  TrendingUp, 
  DollarSign, 
  Target, 
  BarChart3,
  Download,
  Plus,
  Filter,
  RefreshCw,
  Eye,
  Star,
  Check,
  X,
  ArrowUpDown,
  Lightbulb,
  Globe,
  Brain,
  Layers,
  Award,
  Shield,
  Zap,
  PieChart,
  FileText,
  AlertTriangle
} from 'lucide-react';

const EnhancedKeywordResearch = ({ onKeywordSelect, selectedKeywords = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    minVolume: 100,
    maxCpc: 10,
    competition: 'all',
    location: 'US',
    intent: 'all',
    opportunityGrade: 'all'
  });
  const [sortBy, setSortBy] = useState('opportunity_score');
  const [sortOrder, setSortOrder] = useState('desc');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedKeywordIds, setSelectedKeywordIds] = useState(new Set());
  const [analyticsData, setAnalyticsData] = useState(null);
  const [activeTab, setActiveTab] = useState('keywords');
  const [businessType, setBusinessType] = useState('general');

  useEffect(() => {
    if (selectedKeywords.length > 0) {
      setSelectedKeywordIds(new Set(selectedKeywords.map(k => k.id || k.keyword)));
    }
  }, [selectedKeywords]);

  const searchKeywords = async () => {
    if (!searchTerm.trim()) return;
    
    try {
      setLoading(true);
      setError(null);
      
      // First get keywords from research API
      const researchResponse = await fetch('/api/keywords/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          seed_keyword: searchTerm,
          filters: filters,
          limit: 50
        })
      });

      let keywordData = [];
      if (researchResponse.ok) {
        const result = await researchResponse.json();
        if (result.success) {
          keywordData = result.data.keywords || [];
        }
      }

      if (keywordData.length === 0) {
        throw new Error('No keywords found');
      }

      // Enhance with analytics
      const analyticsResponse = await fetch('/api/keyword-analytics/comprehensive-analysis', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          keywords: keywordData,
          business_type: businessType
        })
      });

      if (analyticsResponse.ok) {
        const analyticsResult = await analyticsResponse.json();
        if (analyticsResult.success) {
          setKeywords(analyticsResult.data.keywords);
          setAnalyticsData({
            clusters: analyticsResult.data.clusters,
            negativeKeywords: analyticsResult.data.negative_keywords,
            competitiveAnalysis: analyticsResult.data.competitive_analysis,
            summary: analyticsResult.data.summary
          });
          return;
        }
      }
      
      // Fallback to basic keywords
      setKeywords(keywordData);
      
    } catch (err) {
      console.error('Error fetching keywords:', err);
      setError('Failed to fetch keywords - using demo data');
      
      // Enhanced demo data with analytics
      const demoKeywords = generateEnhancedDemoKeywords(searchTerm);
      setKeywords(demoKeywords);
    } finally {
      setLoading(false);
    }
  };

  const generateEnhancedDemoKeywords = (seed) => {
    const baseKeywords = [
      { 
        base: seed, 
        volume: 45000, 
        cpc: 2.15, 
        competition: 'high', 
        difficulty: 75,
        intent: 'commercial',
        grade: 'B+'
      },
      { 
        base: `${seed} online`, 
        volume: 12000, 
        cpc: 3.20, 
        competition: 'medium', 
        difficulty: 60,
        intent: 'commercial',
        grade: 'A'
      },
      { 
        base: `${seed} near me`, 
        volume: 8500, 
        cpc: 4.50, 
        competition: 'low', 
        difficulty: 45,
        intent: 'navigational',
        grade: 'A+'
      },
      { 
        base: `best ${seed}`, 
        volume: 22000, 
        cpc: 2.80, 
        competition: 'high', 
        difficulty: 70,
        intent: 'commercial',
        grade: 'B'
      },
      { 
        base: `${seed} reviews`, 
        volume: 6700, 
        cpc: 1.90, 
        competition: 'medium', 
        difficulty: 55,
        intent: 'informational',
        grade: 'B+'
      },
      { 
        base: `${seed} price`, 
        volume: 15500, 
        cpc: 2.60, 
        competition: 'medium', 
        difficulty: 50,
        intent: 'commercial',
        grade: 'A'
      },
      { 
        base: `buy ${seed}`, 
        volume: 9800, 
        cpc: 5.20, 
        competition: 'high', 
        difficulty: 80,
        intent: 'transactional',
        grade: 'A+'
      },
      { 
        base: `${seed} comparison`, 
        volume: 4200, 
        cpc: 3.10, 
        competition: 'low', 
        difficulty: 40,
        intent: 'commercial',
        grade: 'A'
      },
      { 
        base: `how to use ${seed}`, 
        volume: 7800, 
        cpc: 1.75, 
        competition: 'low', 
        difficulty: 35,
        intent: 'informational',
        grade: 'B'
      },
      { 
        base: `top ${seed}`, 
        volume: 11200, 
        cpc: 2.95, 
        competition: 'medium', 
        difficulty: 65,
        intent: 'commercial',
        grade: 'B+'
      }
    ];

    return baseKeywords.map((kw, index) => ({
      id: `kw_${Date.now()}_${index}`,
      keyword: kw.base,
      search_volume: kw.volume,
      cpc: kw.cpc,
      competition: kw.competition,
      difficulty: kw.difficulty,
      trend: Math.random() > 0.5 ? 'up' : 'down',
      seasonal: Math.random() > 0.7,
      related_keywords: [`${kw.base} 2024`, `${kw.base} free`, `${kw.base} cost`],
      opportunity_score: Math.round(Math.random() * 40 + 50),
      opportunity_grade: kw.grade,
      search_intent: {
        primary_intent: kw.intent,
        confidence: Math.round(Math.random() * 30 + 70) / 100,
        intent_breakdown: {
          [kw.intent]: Math.round(Math.random() * 30 + 70) / 100,
          'informational': Math.round(Math.random() * 20 + 10) / 100,
          'commercial': Math.round(Math.random() * 20 + 10) / 100,
          'transactional': Math.round(Math.random() * 20 + 10) / 100
        }
      },
      recommendation: "Strong opportunity with good search volume and manageable competition"
    }));
  };

  const exportKeywords = () => {
    const exportData = filteredKeywords.map(kw => ({
      Keyword: kw.keyword,
      'Search Volume': kw.search_volume,
      CPC: kw.cpc,
      Competition: kw.competition,
      Difficulty: kw.difficulty,
      'Opportunity Score': kw.opportunity_score,
      Grade: kw.opportunity_grade,
      'Primary Intent': kw.search_intent?.primary_intent,
      Recommendation: kw.recommendation
    }));

    const csvContent = [
      Object.keys(exportData[0]).join(','),
      ...exportData.map(row => Object.values(row).join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `keyword-research-${searchTerm}-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
  };

  const toggleKeywordSelection = (keyword) => {
    const newSelected = new Set(selectedKeywordIds);
    const keywordId = keyword.id || keyword.keyword;
    
    if (newSelected.has(keywordId)) {
      newSelected.delete(keywordId);
    } else {
      newSelected.add(keywordId);
    }
    
    setSelectedKeywordIds(newSelected);
    
    if (onKeywordSelect) {
      const selectedKeywordsList = keywords.filter(k => 
        newSelected.has(k.id || k.keyword)
      );
      onKeywordSelect(selectedKeywordsList);
    }
  };

  const sortedKeywords = [...keywords].sort((a, b) => {
    let aVal, bVal;
    
    switch (sortBy) {
      case 'volume':
        aVal = a.search_volume;
        bVal = b.search_volume;
        break;
      case 'cpc':
        aVal = a.cpc;
        bVal = b.cpc;
        break;
      case 'difficulty':
        aVal = a.difficulty;
        bVal = b.difficulty;
        break;
      case 'opportunity_score':
        aVal = a.opportunity_score || 0;
        bVal = b.opportunity_score || 0;
        break;
      default:
        aVal = a.keyword;
        bVal = b.keyword;
    }
    
    if (sortOrder === 'asc') {
      return aVal > bVal ? 1 : -1;
    } else {
      return aVal < bVal ? 1 : -1;
    }
  });

  const filteredKeywords = sortedKeywords.filter(keyword => {
    if (keyword.search_volume < filters.minVolume) return false;
    if (keyword.cpc > filters.maxCpc) return false;
    if (filters.competition !== 'all' && keyword.competition !== filters.competition) return false;
    if (filters.intent !== 'all' && keyword.search_intent?.primary_intent !== filters.intent) return false;
    if (filters.opportunityGrade !== 'all' && keyword.opportunity_grade !== filters.opportunityGrade) return false;
    return true;
  });

  const getGradeColor = (grade) => {
    const gradeColors = {
      'A+': '#10b981',
      'A': '#059669',
      'B+': '#3b82f6',
      'B': '#2563eb',
      'C': '#f59e0b',
      'D': '#ef4444'
    };
    return gradeColors[grade] || '#6b7280';
  };

  const getIntentColor = (intent) => {
    const intentColors = {
      'commercial': '#8b5cf6',
      'transactional': '#10b981',
      'informational': '#3b82f6',
      'navigational': '#f59e0b'
    };
    return intentColors[intent] || '#6b7280';
  };

  const renderKeywordClusters = () => {
    if (!analyticsData?.clusters) return null;

    return (
      <div style={{ padding: '1rem 2rem' }}>
        <h3 style={{ color: '#111827', marginBottom: '1rem' }}>Keyword Clusters</h3>
        <div style={{ display: 'grid', gap: '1rem' }}>
          {Object.entries(analyticsData.clusters).map(([clusterName, cluster]) => (
            <div
              key={clusterName}
              style={{
                background: 'rgba(255, 255, 255, 0.4)',
                borderRadius: '12px',
                padding: '1rem',
                border: '1px solid rgba(255, 255, 255, 0.3)'
              }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <h4 style={{ color: '#111827', margin: 0 }}>{clusterName}</h4>
                <div style={{ 
                  background: getGradeColor(cluster.opportunity_score >= 80 ? 'A+' : cluster.opportunity_score >= 60 ? 'B+' : 'C'),
                  color: 'white',
                  padding: '2px 8px',
                  borderRadius: '12px',
                  fontSize: '0.75rem'
                }}>
                  Score: {cluster.opportunity_score}
                </div>
              </div>
              
              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))',
                gap: '0.5rem',
                fontSize: '0.875rem',
                marginBottom: '0.5rem'
              }}>
                <div>
                  <span style={{ color: '#6b7280' }}>Keywords: </span>
                  <span style={{ fontWeight: '600' }}>{cluster.keyword_count}</span>
                </div>
                <div>
                  <span style={{ color: '#6b7280' }}>Volume: </span>
                  <span style={{ fontWeight: '600' }}>{cluster.total_volume.toLocaleString()}</span>
                </div>
                <div>
                  <span style={{ color: '#6b7280' }}>Avg CPC: </span>
                  <span style={{ fontWeight: '600' }}>${cluster.average_cpc}</span>
                </div>
                <div>
                  <span style={{ color: '#6b7280' }}>Avg Difficulty: </span>
                  <span style={{ fontWeight: '600' }}>{cluster.average_difficulty}</span>
                </div>
              </div>
              
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                {cluster.keywords.slice(0, 5).map((kw, idx) => (
                  <span
                    key={idx}
                    style={{
                      background: 'rgba(99, 102, 241, 0.1)',
                      color: '#6366f1',
                      padding: '2px 6px',
                      borderRadius: '6px',
                      fontSize: '0.75rem'
                    }}
                  >
                    {kw.keyword}
                  </span>
                ))}
                {cluster.keywords.length > 5 && (
                  <span style={{ color: '#6b7280', fontSize: '0.75rem' }}>
                    +{cluster.keywords.length - 5} more
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderNegativeKeywords = () => {
    if (!analyticsData?.negativeKeywords) return null;

    return (
      <div style={{ padding: '1rem 2rem' }}>
        <h3 style={{ color: '#111827', marginBottom: '1rem' }}>Negative Keyword Suggestions</h3>
        <div style={{ display: 'grid', gap: '0.5rem' }}>
          {analyticsData.negativeKeywords.map((negative, idx) => (
            <div
              key={idx}
              style={{
                background: 'rgba(239, 68, 68, 0.1)',
                borderRadius: '8px',
                padding: '0.75rem',
                border: '1px solid rgba(239, 68, 68, 0.2)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}
            >
              <div>
                <div style={{ fontWeight: '600', color: '#dc2626' }}>
                  {negative.keyword} ({negative.match_type})
                </div>
                <div style={{ fontSize: '0.75rem', color: '#6b7280' }}>
                  {negative.reason}
                </div>
              </div>
              <div style={{
                background: `rgba(220, 38, 38, ${negative.confidence})`,
                color: 'white',
                padding: '2px 6px',
                borderRadius: '6px',
                fontSize: '0.75rem'
              }}>
                {Math.round(negative.confidence * 100)}%
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderAnalyticsSummary = () => {
    if (!analyticsData?.summary) return null;

    const summary = analyticsData.summary;

    return (
      <div style={{ padding: '1rem 2rem', borderBottom: '1px solid rgba(255, 255, 255, 0.2)' }}>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
          gap: '1rem'
        }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ color: '#6366f1', fontSize: '1.5rem', fontWeight: '700' }}>
              {summary.total_keywords}
            </div>
            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>
              Total Keywords
            </div>
          </div>
          
          <div style={{ textAlign: 'center' }}>
            <div style={{ color: '#10b981', fontSize: '1.5rem', fontWeight: '700' }}>
              {summary.high_opportunity_keywords}
            </div>
            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>
              High Opportunity
            </div>
          </div>
          
          <div style={{ textAlign: 'center' }}>
            <div style={{ color: '#8b5cf6', fontSize: '1.5rem', fontWeight: '700' }}>
              {summary.total_clusters}
            </div>
            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>
              Keyword Clusters
            </div>
          </div>
          
          <div style={{ textAlign: 'center' }}>
            <div style={{ color: '#f59e0b', fontSize: '1.5rem', fontWeight: '700' }}>
              {summary.average_opportunity_score}
            </div>
            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>
              Avg Opportunity Score
            </div>
          </div>
        </div>
      </div>
    );
  };

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
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1rem'
        }}>
          <div>
            <h2 style={{
              color: '#111827',
              fontSize: '1.5rem',
              fontWeight: '700',
              margin: '0 0 0.5rem 0'
            }}>
              <Brain size={24} style={{ display: 'inline', marginRight: '8px', color: '#6366f1' }} />
              AI-Powered Keyword Intelligence
            </h2>
            <p style={{
              color: '#6b7280',
              fontSize: '0.875rem',
              margin: 0
            }}>
              Enterprise keyword research with clustering, intent analysis, and competitive insights
            </p>
          </div>
          
          <div style={{ display: 'flex', gap: '8px' }}>
            <select
              value={businessType}
              onChange={(e) => setBusinessType(e.target.value)}
              style={{
                padding: '8px 12px',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.8)',
                fontSize: '0.875rem'
              }}
            >
              <option value="general">General</option>
              <option value="ecommerce">E-commerce</option>
              <option value="b2b">B2B</option>
              <option value="service">Service</option>
            </select>
            
            <button
              onClick={() => setShowFilters(!showFilters)}
              style={{
                background: showFilters 
                  ? 'rgba(99, 102, 241, 0.2)' 
                  : 'rgba(255, 255, 255, 0.8)',
                border: '1px solid rgba(255, 255, 255, 0.5)',
                borderRadius: '8px',
                padding: '8px 12px',
                cursor: 'pointer',
                color: showFilters ? '#6366f1' : '#374151',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <Filter size={16} />
              Advanced Filters
            </button>
            
            {keywords.length > 0 && (
              <button
                onClick={exportKeywords}
                style={{
                  background: 'rgba(255, 255, 255, 0.8)',
                  border: '1px solid rgba(255, 255, 255, 0.5)',
                  borderRadius: '8px',
                  padding: '8px 12px',
                  cursor: 'pointer',
                  color: '#374151',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <Download size={16} />
                Export
              </button>
            )}
          </div>
        </div>

        {/* Search Interface */}
        <div style={{
          display: 'flex',
          gap: '12px',
          alignItems: 'center'
        }}>
          <div style={{
            flex: 1,
            position: 'relative'
          }}>
            <Search 
              size={20} 
              style={{
                position: 'absolute',
                left: '12px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: '#6b7280'
              }} 
            />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && searchKeywords()}
              placeholder="Enter seed keyword for AI-powered analysis..."
              style={{
                width: '100%',
                padding: '12px 12px 12px 44px',
                border: '1px solid rgba(255, 255, 255, 0.3)',
                borderRadius: '12px',
                background: 'rgba(255, 255, 255, 0.5)',
                fontSize: '1rem',
                outline: 'none'
              }}
            />
          </div>
          
          <button
            onClick={searchKeywords}
            disabled={loading || !searchTerm.trim()}
            style={{
              background: loading 
                ? 'rgba(107, 114, 128, 0.5)' 
                : 'linear-gradient(135deg, #6366f1, #8b5cf6)',
              color: 'white',
              border: 'none',
              borderRadius: '12px',
              padding: '12px 20px',
              cursor: loading ? 'not-allowed' : 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontWeight: '600'
            }}
          >
            {loading ? <RefreshCw size={20} className="animate-spin" /> : <Brain size={20} />}
            Analyze
          </button>
        </div>
      </div>

      {/* Enhanced Filters Panel */}
      {showFilters && (
        <div style={{
          padding: '1rem 2rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
          background: 'rgba(255, 255, 255, 0.3)'
        }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))',
            gap: '1rem'
          }}>
            <div>
              <label style={{ color: '#374151', fontSize: '0.875rem', fontWeight: '600' }}>
                Min Search Volume
              </label>
              <input
                type="number"
                value={filters.minVolume}
                onChange={(e) => setFilters(prev => ({ ...prev, minVolume: parseInt(e.target.value) || 0 }))}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: '6px',
                  background: 'rgba(255, 255, 255, 0.5)',
                  marginTop: '4px'
                }}
              />
            </div>
            
            <div>
              <label style={{ color: '#374151', fontSize: '0.875rem', fontWeight: '600' }}>
                Max CPC ($)
              </label>
              <input
                type="number"
                step="0.1"
                value={filters.maxCpc}
                onChange={(e) => setFilters(prev => ({ ...prev, maxCpc: parseFloat(e.target.value) || 0 }))}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: '6px',
                  background: 'rgba(255, 255, 255, 0.5)',
                  marginTop: '4px'
                }}
              />
            </div>
            
            <div>
              <label style={{ color: '#374151', fontSize: '0.875rem', fontWeight: '600' }}>
                Competition Level
              </label>
              <select
                value={filters.competition}
                onChange={(e) => setFilters(prev => ({ ...prev, competition: e.target.value }))}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: '6px',
                  background: 'rgba(255, 255, 255, 0.5)',
                  marginTop: '4px'
                }}
              >
                <option value="all">All</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
              </select>
            </div>
            
            <div>
              <label style={{ color: '#374151', fontSize: '0.875rem', fontWeight: '600' }}>
                Search Intent
              </label>
              <select
                value={filters.intent}
                onChange={(e) => setFilters(prev => ({ ...prev, intent: e.target.value }))}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: '6px',
                  background: 'rgba(255, 255, 255, 0.5)',
                  marginTop: '4px'
                }}
              >
                <option value="all">All Intents</option>
                <option value="commercial">Commercial</option>
                <option value="transactional">Transactional</option>
                <option value="informational">Informational</option>
                <option value="navigational">Navigational</option>
              </select>
            </div>
            
            <div>
              <label style={{ color: '#374151', fontSize: '0.875rem', fontWeight: '600' }}>
                Opportunity Grade
              </label>
              <select
                value={filters.opportunityGrade}
                onChange={(e) => setFilters(prev => ({ ...prev, opportunityGrade: e.target.value }))}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: '6px',
                  background: 'rgba(255, 255, 255, 0.5)',
                  marginTop: '4px'
                }}
              >
                <option value="all">All Grades</option>
                <option value="A+">A+ Only</option>
                <option value="A">A or Higher</option>
                <option value="B+">B+ or Higher</option>
                <option value="B">B or Higher</option>
              </select>
            </div>
          </div>
        </div>
      )}

      {/* Analytics Summary */}
      {analyticsData && renderAnalyticsSummary()}

      {/* Tab Navigation */}
      {keywords.length > 0 && (
        <div style={{
          display: 'flex',
          borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
          background: 'rgba(255, 255, 255, 0.1)'
        }}>
          {[
            { id: 'keywords', label: 'Keywords', icon: Search },
            { id: 'clusters', label: 'Clusters', icon: Layers },
            { id: 'negatives', label: 'Negatives', icon: Shield }
          ].map(tab => {
            const IconComponent = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  background: activeTab === tab.id ? 'rgba(99, 102, 241, 0.2)' : 'transparent',
                  border: 'none',
                  padding: '12px 20px',
                  color: activeTab === tab.id ? '#6366f1' : '#6b7280',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  fontSize: '0.875rem',
                  fontWeight: '600'
                }}
              >
                <IconComponent size={16} />
                {tab.label}
              </button>
            );
          })}
        </div>
      )}

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
          <AlertTriangle size={16} color="#dc2626" />
          <span style={{ color: '#dc2626', fontSize: '0.875rem' }}>
            {error}
          </span>
        </div>
      )}

      {/* Content based on active tab */}
      {loading ? (
        <div style={{
          padding: '3rem 2rem',
          textAlign: 'center'
        }}>
          <Brain size={48} style={{ color: '#6366f1', animation: 'spin 1s linear infinite' }} />
          <h3 style={{ color: '#111827', marginTop: '1rem' }}>Analyzing Keywords with AI...</h3>
          <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Processing search volume, competition, intent classification, and opportunity scoring
          </p>
        </div>
      ) : (
        <>
          {activeTab === 'keywords' && filteredKeywords.length > 0 && (
            <>
              {/* Results Header */}
              <div style={{
                padding: '1rem 2rem',
                borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <div>
                  <h3 style={{
                    color: '#111827',
                    fontSize: '1.125rem',
                    fontWeight: '600',
                    margin: '0 0 0.25rem 0'
                  }}>
                    Enhanced Keyword Analysis
                  </h3>
                  <p style={{
                    color: '#6b7280',
                    fontSize: '0.875rem',
                    margin: 0
                  }}>
                    {filteredKeywords.length} keywords with AI-powered insights
                  </p>
                </div>
                
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <span style={{ color: '#6b7280', fontSize: '0.875rem' }}>Sort by:</span>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    style={{
                      padding: '4px 8px',
                      border: '1px solid rgba(255, 255, 255, 0.3)',
                      borderRadius: '6px',
                      background: 'rgba(255, 255, 255, 0.5)',
                      fontSize: '0.875rem'
                    }}
                  >
                    <option value="opportunity_score">Opportunity Score</option>
                    <option value="volume">Search Volume</option>
                    <option value="cpc">CPC</option>
                    <option value="difficulty">Difficulty</option>
                    <option value="keyword">Keyword</option>
                  </select>
                  
                  <button
                    onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                    style={{
                      background: 'rgba(255, 255, 255, 0.8)',
                      border: '1px solid rgba(255, 255, 255, 0.5)',
                      borderRadius: '6px',
                      padding: '4px',
                      cursor: 'pointer'
                    }}
                  >
                    <ArrowUpDown size={16} color="#6b7280" />
                  </button>
                </div>
              </div>

              {/* Enhanced Keywords List */}
              <div style={{ padding: '1rem 2rem' }}>
                <div style={{ display: 'grid', gap: '0.75rem' }}>
                  {filteredKeywords.map((keyword) => {
                    const isSelected = selectedKeywordIds.has(keyword.id || keyword.keyword);
                    
                    return (
                      <div
                        key={keyword.id || keyword.keyword}
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
                        onClick={() => toggleKeywordSelection(keyword)}
                      >
                        <div style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'flex-start'
                        }}>
                          <div style={{ flex: 1 }}>
                            <div style={{
                              display: 'flex',
                              alignItems: 'center',
                              gap: '8px',
                              marginBottom: '0.5rem'
                            }}>
                              <span style={{
                                color: '#111827',
                                fontWeight: '600',
                                fontSize: '1rem'
                              }}>
                                {keyword.keyword}
                              </span>
                              
                              {keyword.opportunity_grade && (
                                <span style={{
                                  background: getGradeColor(keyword.opportunity_grade),
                                  color: 'white',
                                  padding: '2px 6px',
                                  borderRadius: '6px',
                                  fontSize: '0.75rem',
                                  fontWeight: '600'
                                }}>
                                  {keyword.opportunity_grade}
                                </span>
                              )}
                              
                              {keyword.search_intent && (
                                <span style={{
                                  background: getIntentColor(keyword.search_intent.primary_intent),
                                  color: 'white',
                                  padding: '2px 6px',
                                  borderRadius: '6px',
                                  fontSize: '0.75rem',
                                  fontWeight: '600'
                                }}>
                                  {keyword.search_intent.primary_intent}
                                </span>
                              )}
                              
                              {keyword.trend === 'up' && (
                                <TrendingUp size={16} color="#10b981" />
                              )}
                              
                              {keyword.seasonal && (
                                <Star size={16} color="#f59e0b" />
                              )}
                            </div>
                            
                            <div style={{
                              display: 'grid',
                              gridTemplateColumns: 'repeat(auto-fit, minmax(100px, 1fr))',
                              gap: '1rem',
                              fontSize: '0.875rem',
                              marginBottom: '0.5rem'
                            }}>
                              <div>
                                <div style={{ color: '#6b7280', fontSize: '0.75rem' }}>Volume</div>
                                <div style={{ color: '#111827', fontWeight: '600' }}>
                                  {keyword.search_volume.toLocaleString()}
                                </div>
                              </div>
                              
                              <div>
                                <div style={{ color: '#6b7280', fontSize: '0.75rem' }}>CPC</div>
                                <div style={{ color: '#111827', fontWeight: '600' }}>
                                  ${keyword.cpc.toFixed(2)}
                                </div>
                              </div>
                              
                              <div>
                                <div style={{ color: '#6b7280', fontSize: '0.75rem' }}>Difficulty</div>
                                <div style={{ color: '#111827', fontWeight: '600' }}>
                                  {keyword.difficulty}/100
                                </div>
                              </div>
                              
                              {keyword.opportunity_score && (
                                <div>
                                  <div style={{ color: '#6b7280', fontSize: '0.75rem' }}>Opportunity</div>
                                  <div style={{ 
                                    color: getGradeColor(keyword.opportunity_grade), 
                                    fontWeight: '600' 
                                  }}>
                                    {keyword.opportunity_score}/100
                                  </div>
                                </div>
                              )}
                            </div>
                            
                            {keyword.recommendation && (
                              <div style={{
                                fontSize: '0.75rem',
                                color: '#6b7280',
                                fontStyle: 'italic'
                              }}>
                                💡 {keyword.recommendation}
                              </div>
                            )}
                          </div>
                          
                          <div style={{
                            width: '24px',
                            height: '24px',
                            borderRadius: '50%',
                            border: isSelected 
                              ? '2px solid #6366f1'
                              : '2px solid rgba(107, 114, 128, 0.3)',
                            background: isSelected ? '#6366f1' : 'transparent',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            transition: 'all 0.3s ease'
                          }}>
                            {isSelected && <Check size={14} color="white" />}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </>
          )}
          
          {activeTab === 'clusters' && renderKeywordClusters()}
          {activeTab === 'negatives' && renderNegativeKeywords()}
        </>
      )}

      {/* Empty State */}
      {!loading && keywords.length === 0 && (
        <div style={{
          padding: '3rem 2rem',
          textAlign: 'center'
        }}>
          <Brain size={48} color="#6b7280" />
          <h3 style={{ color: '#111827', marginTop: '1rem' }}>Start Your AI-Powered Keyword Research</h3>
          <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Enter a seed keyword to discover insights with clustering, intent analysis, and opportunity scoring
          </p>
        </div>
      )}
    </div>
  );
};

export default EnhancedKeywordResearch;