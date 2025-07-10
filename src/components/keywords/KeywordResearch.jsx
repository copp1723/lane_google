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
  Globe
} from 'lucide-react';

const KeywordResearch = ({ onKeywordSelect, selectedKeywords = [] }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [keywords, setKeywords] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    minVolume: 100,
    maxCpc: 10,
    competition: 'all',
    location: 'US'
  });
  const [sortBy, setSortBy] = useState('volume');
  const [sortOrder, setSortOrder] = useState('desc');
  const [showFilters, setShowFilters] = useState(false);
  const [selectedKeywordIds, setSelectedKeywordIds] = useState(new Set());

  useEffect(() => {
    // Load any previously selected keywords
    if (selectedKeywords.length > 0) {
      setSelectedKeywordIds(new Set(selectedKeywords.map(k => k.id || k.keyword)));
    }
  }, [selectedKeywords]);

  const searchKeywords = async () => {
    if (!searchTerm.trim()) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/keywords/research', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          seed_keyword: searchTerm,
          filters: filters,
          limit: 50
        })
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setKeywords(result.data.keywords || []);
          return;
        }
      }
      
      throw new Error('Failed to fetch keywords');
    } catch (err) {
      console.error('Error fetching keywords:', err);
      setError('Failed to fetch keywords - using demo data');
      
      // Demo data with realistic keyword metrics
      const demoKeywords = generateDemoKeywords(searchTerm);
      setKeywords(demoKeywords);
    } finally {
      setLoading(false);
    }
  };

  const generateDemoKeywords = (seed) => {
    const baseKeywords = [
      { base: seed, volume: 45000, cpc: 2.15, competition: 'high', difficulty: 75 },
      { base: `${seed} online`, volume: 12000, cpc: 3.20, competition: 'medium', difficulty: 60 },
      { base: `${seed} near me`, volume: 8500, cpc: 4.50, competition: 'low', difficulty: 45 },
      { base: `best ${seed}`, volume: 22000, cpc: 2.80, competition: 'high', difficulty: 70 },
      { base: `${seed} reviews`, volume: 6700, cpc: 1.90, competition: 'medium', difficulty: 55 },
      { base: `${seed} price`, volume: 15500, cpc: 2.60, competition: 'medium', difficulty: 50 },
      { base: `buy ${seed}`, volume: 9800, cpc: 5.20, competition: 'high', difficulty: 80 },
      { base: `${seed} comparison`, volume: 4200, cpc: 3.10, competition: 'low', difficulty: 40 },
      { base: `${seed} guide`, volume: 7800, cpc: 1.75, competition: 'low', difficulty: 35 },
      { base: `top ${seed}`, volume: 11200, cpc: 2.95, competition: 'medium', difficulty: 65 }
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
      related_keywords: [`${kw.base} 2024`, `${kw.base} free`, `${kw.base} cost`]
    }));
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
    return true;
  });

  const getCompetitionColor = (competition) => {
    switch (competition) {
      case 'low': return '#10b981';
      case 'medium': return '#f59e0b';
      case 'high': return '#ef4444';
      default: return '#6b7280';
    }
  };

  const getDifficultyColor = (difficulty) => {
    if (difficulty <= 30) return '#10b981';
    if (difficulty <= 60) return '#f59e0b';
    return '#ef4444';
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
              Keyword Research
            </h2>
            <p style={{
              color: '#6b7280',
              fontSize: '0.875rem',
              margin: 0
            }}>
              Discover high-performing keywords for your campaigns
            </p>
          </div>
          
          <div style={{ display: 'flex', gap: '8px' }}>
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
              Filters
            </button>
            
            {selectedKeywordIds.size > 0 && (
              <button
                style={{
                  background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '8px 12px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
              >
                <Check size={16} />
                {selectedKeywordIds.size} Selected
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
              placeholder="Enter seed keyword (e.g., 'fitness equipment', 'digital marketing')..."
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
            {loading ? <RefreshCw size={20} className="animate-spin" /> : <Search size={20} />}
            Search
          </button>
        </div>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <div style={{
          padding: '1rem 2rem',
          borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
          background: 'rgba(255, 255, 255, 0.3)'
        }}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
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
                Location
              </label>
              <select
                value={filters.location}
                onChange={(e) => setFilters(prev => ({ ...prev, location: e.target.value }))}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  border: '1px solid rgba(255, 255, 255, 0.3)',
                  borderRadius: '6px',
                  background: 'rgba(255, 255, 255, 0.5)',
                  marginTop: '4px'
                }}
              >
                <option value="US">United States</option>
                <option value="UK">United Kingdom</option>
                <option value="CA">Canada</option>
                <option value="AU">Australia</option>
                <option value="global">Global</option>
              </select>
            </div>
          </div>
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
          <Lightbulb size={16} color="#dc2626" />
          <span style={{ color: '#dc2626', fontSize: '0.875rem' }}>
            {error}
          </span>
        </div>
      )}

      {/* Results Header */}
      {keywords.length > 0 && (
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
              Keyword Results
            </h3>
            <p style={{
              color: '#6b7280',
              fontSize: '0.875rem',
              margin: 0
            }}>
              Found {filteredKeywords.length} keywords matching your criteria
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
      )}

      {/* Keywords List */}
      {loading ? (
        <div style={{
          padding: '3rem 2rem',
          textAlign: 'center'
        }}>
          <RefreshCw size={48} style={{ color: '#6366f1', animation: 'spin 1s linear infinite' }} />
          <h3 style={{ color: '#111827', marginTop: '1rem' }}>Researching Keywords...</h3>
          <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Analyzing search volume, competition, and trends
          </p>
        </div>
      ) : filteredKeywords.length > 0 ? (
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
                        
                        {keyword.trend === 'up' && (
                          <TrendingUp size={16} color="#10b981" />
                        )}
                        
                        {keyword.seasonal && (
                          <Star size={16} color="#f59e0b" />
                        )}
                      </div>
                      
                      <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                        gap: '1rem',
                        fontSize: '0.875rem'
                      }}>
                        <div>
                          <div style={{ color: '#6b7280', fontSize: '0.75rem' }}>Search Volume</div>
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
                          <div style={{ color: '#6b7280', fontSize: '0.75rem' }}>Competition</div>
                          <div style={{ 
                            color: getCompetitionColor(keyword.competition), 
                            fontWeight: '600',
                            textTransform: 'capitalize'
                          }}>
                            {keyword.competition}
                          </div>
                        </div>
                        
                        <div>
                          <div style={{ color: '#6b7280', fontSize: '0.75rem' }}>Difficulty</div>
                          <div style={{ 
                            color: getDifficultyColor(keyword.difficulty), 
                            fontWeight: '600' 
                          }}>
                            {keyword.difficulty}/100
                          </div>
                        </div>
                      </div>
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
      ) : searchTerm && !loading ? (
        <div style={{
          padding: '3rem 2rem',
          textAlign: 'center'
        }}>
          <Search size={48} color="#6b7280" />
          <h3 style={{ color: '#111827', marginTop: '1rem' }}>No Keywords Found</h3>
          <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Try adjusting your search term or filters
          </p>
        </div>
      ) : (
        <div style={{
          padding: '3rem 2rem',
          textAlign: 'center'
        }}>
          <Lightbulb size={48} color="#6b7280" />
          <h3 style={{ color: '#111827', marginTop: '1rem' }}>Start Your Keyword Research</h3>
          <p style={{ color: '#6b7280', fontSize: '0.875rem' }}>
            Enter a seed keyword above to discover related keywords with search volume, CPC, and competition data
          </p>
        </div>
      )}
    </div>
  );
};

export default KeywordResearch;