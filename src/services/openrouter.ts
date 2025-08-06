import axios from 'axios';
import { z } from 'zod';
import { logger } from '../utils/logger';
import { AppError, ErrorType } from '../middleware/error-handler';

// OpenRouter API types
export const chatRequestSchema = z.object({
  message: z.string().min(1).max(10000),
  model: z.string().default('anthropic/claude-3.5-sonnet'),
  temperature: z.number().min(0).max(2).default(0.7),
  maxTokens: z.number().min(1).max(100000).default(4000),
  systemPrompt: z.string().optional(),
  stream: z.boolean().default(false)
});

export type ChatRequest = z.infer<typeof chatRequestSchema>;

interface OpenRouterResponse {
  id: string;
  choices: Array<{
    message: {
      role: string;
      content: string;
    };
    finish_reason: string;
  }>;
  usage: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
  model: string;
}

export class OpenRouterService {
  private readonly apiKey: string;
  private readonly baseUrl: string;
  private readonly siteUrl: string;
  private readonly siteName: string;

  constructor() {
    this.apiKey = import.meta.env.VITE_OPENROUTER_API_KEY || '';
    this.baseUrl = import.meta.env.VITE_OPENROUTER_BASE_URL || 'https://openrouter.ai/api/v1';
    this.siteUrl = import.meta.env.VITE_SITE_URL || 'http://localhost:3000';
    this.siteName = import.meta.env.VITE_SITE_NAME || 'Lane MCP';

    if (!this.apiKey) {
      logger.warn('OpenRouter API key not configured');
    }
  }

  async chat(request: ChatRequest): Promise<OpenRouterResponse> {
    if (!this.apiKey) {
      throw new AppError(
        'OpenRouter API key not configured',
        ErrorType.EXTERNAL_API,
        503,
        true
      );
    }

    try {
      const messages = [];
      
      if (request.systemPrompt) {
        messages.push({
          role: 'system',
          content: request.systemPrompt
        });
      }
      
      messages.push({
        role: 'user',
        content: request.message
      });

      const response = await axios.post(
        `${this.baseUrl}/chat/completions`,
        {
          model: request.model,
          messages,
          temperature: request.temperature,
          max_tokens: request.maxTokens,
          stream: false // We'll handle streaming separately
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'HTTP-Referer': this.siteUrl,
            'X-Title': this.siteName,
            'Content-Type': 'application/json'
          },
          timeout: 30000
        }
      );

      logger.info('OpenRouter API call successful', {
        model: request.model,
        usage: response.data.usage
      });

      return response.data;
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status || 500;
        const message = error.response?.data?.error?.message || error.message;
        
        logger.error('OpenRouter API error', {
          status,
          message,
          model: request.model
        });

        throw new AppError(
          `OpenRouter API error: ${message}`,
          ErrorType.EXTERNAL_API,
          status,
          true,
          { originalError: message }
        );
      }

      throw error;
    }
  }

  async *chatStream(request: ChatRequest): AsyncGenerator<string> {
    if (!this.apiKey) {
      throw new AppError(
        'OpenRouter API key not configured',
        ErrorType.EXTERNAL_API,
        503,
        true
      );
    }

    try {
      const messages = [];
      
      if (request.systemPrompt) {
        messages.push({
          role: 'system',
          content: request.systemPrompt
        });
      }
      
      messages.push({
        role: 'user',
        content: request.message
      });

      const response = await axios.post(
        `${this.baseUrl}/chat/completions`,
        {
          model: request.model,
          messages,
          temperature: request.temperature,
          max_tokens: request.maxTokens,
          stream: true
        },
        {
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'HTTP-Referer': this.siteUrl,
            'X-Title': this.siteName,
            'Content-Type': 'application/json'
          },
          responseType: 'stream',
          timeout: 60000
        }
      );

      const stream = response.data;
      let buffer = '';

      for await (const chunk of stream) {
        buffer += chunk.toString();
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmedLine = line.trim();
          if (trimmedLine === '' || trimmedLine === 'data: [DONE]') continue;
          
          if (trimmedLine.startsWith('data: ')) {
            try {
              const data = JSON.parse(trimmedLine.slice(6));
              const content = data.choices?.[0]?.delta?.content;
              if (content) {
                yield content;
              }
            } catch (e) {
              logger.warn('Failed to parse SSE data', { line: trimmedLine });
            }
          }
        }
      }
    } catch (error) {
      if (axios.isAxiosError(error)) {
        const status = error.response?.status || 500;
        const message = error.response?.data?.error?.message || error.message;
        
        logger.error('OpenRouter streaming error', {
          status,
          message,
          model: request.model
        });

        throw new AppError(
          `OpenRouter streaming error: ${message}`,
          ErrorType.EXTERNAL_API,
          status,
          true,
          { originalError: message }
        );
      }

      throw error;
    }
  }

  async getModels(): Promise<any[]> {
    try {
      const response = await axios.get(`${this.baseUrl}/models`, {
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'HTTP-Referer': this.siteUrl,
          'X-Title': this.siteName
        },
        timeout: 10000
      });

      return response.data.data || [];
    } catch (error) {
      logger.error('Failed to fetch OpenRouter models', {
        error: error instanceof Error ? error.message : 'Unknown error'
      });

      // Return default models if API fails
      return [
        {
          id: 'anthropic/claude-3.5-sonnet',
          name: 'Claude 3.5 Sonnet',
          context_length: 200000,
          pricing: { prompt: 0.003, completion: 0.015 }
        },
        {
          id: 'openai/gpt-4-turbo-preview',
          name: 'GPT-4 Turbo',
          context_length: 128000,
          pricing: { prompt: 0.01, completion: 0.03 }
        },
        {
          id: 'google/gemini-pro-1.5',
          name: 'Gemini Pro 1.5',
          context_length: 1000000,
          pricing: { prompt: 0.0025, completion: 0.0075 }
        }
      ];
    }
  }

  calculateCost(usage: { prompt_tokens: number; completion_tokens: number }, model: string): number {
    // Basic cost calculation - you should fetch actual pricing from OpenRouter
    const pricing: Record<string, { prompt: number; completion: number }> = {
      'anthropic/claude-3.5-sonnet': { prompt: 0.003, completion: 0.015 },
      'openai/gpt-4-turbo-preview': { prompt: 0.01, completion: 0.03 },
      'openai/gpt-3.5-turbo': { prompt: 0.0005, completion: 0.0015 },
      'google/gemini-pro-1.5': { prompt: 0.0025, completion: 0.0075 }
    };

    const modelPricing = pricing[model] || { prompt: 0.001, completion: 0.002 };
    
    return (
      (usage.prompt_tokens / 1000) * modelPricing.prompt +
      (usage.completion_tokens / 1000) * modelPricing.completion
    );
  }
}

export const openRouterService = new OpenRouterService();