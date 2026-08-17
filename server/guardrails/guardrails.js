/**
 * Guardrails — Voice RAG 2026
 *
 * A. Off-topic guardrail
 * B. Unsafe/inappropriate input guardrail
 * C. Retrieval-empty guardrail (handled in model harness)
 * D. Grounding guardrail
 * E. Citation guardrail
 * F. Prompt injection defense
 * G. Output guardrail
 * H. Refusal state
 */

class Guardrails {
  constructor() {
    // Unsafe patterns
    this._unsafePatterns = [
      /how\s+to\s+(make|build|create)\s+(a\s+)?(bomb|weapon|explosive|drug)/i,
      /hack\s+(into|a|the)\s+/i,
      /steal\s+(money|data|identity)/i,
      /\b(kill|murder|harm|hurt|attack)\s+(someone|a\s+person|people)/i,
      /illegal\s+(activity|drug|weapon)/i,
      /\b(child|minor)\s*(abuse|exploit|porn)/i,
    ];

    // Prompt injection patterns
    this._injectionPatterns = [
      /ignore\s+(all\s+)?previous\s+instructions/i,
      /forget\s+(all\s+)?your\s+(rules|instructions|guidelines)/i,
      /you\s+are\s+now\s+(a|an)\s/i,
      /system\s*prompt/i,
      /\bDAN\b.*\bjailbreak\b/i,
      /pretend\s+you\s+(are|have|can)/i,
      /act\s+as\s+(if|though)\s+you/i,
      /override\s+(your|the)\s+(safety|rules|guidelines)/i,
      /new\s+instructions?\s*:/i,
      /\[SYSTEM\]/i,
      /\[INST\]/i,
    ];

    // Off-topic detection requires domain context
    this._domainKeywords = new Set();
  }

  /**
   * Set domain keywords for off-topic detection
   * @param {string[]} keywords
   */
  setDomainKeywords(keywords) {
    this._domainKeywords = new Set(keywords.map(k => k.toLowerCase()));
  }

  /**
   * A. Off-topic guardrail
   * @param {string} query
   * @returns {{isOffTopic: boolean, message?: string}}
   */
  checkOffTopic(query) {
    // If no domain keywords set, allow all queries (knowledge base may be general)
    if (this._domainKeywords.size === 0) {
      return { isOffTopic: false };
    }

    const words = query.toLowerCase().split(/\s+/);
    const hasRelevantWord = words.some(w => {
      for (const keyword of this._domainKeywords) {
        if (w.includes(keyword) || keyword.includes(w)) return true;
      }
      return false;
    });

    if (!hasRelevantWord && words.length > 3) {
      return {
        isOffTopic: true,
        message: 'Your question doesn\'t appear to be related to the available knowledge base. Please ask about the topics covered in the uploaded documents.'
      };
    }

    return { isOffTopic: false };
  }

  /**
   * B. Unsafe/inappropriate input guardrail
   * @param {string} query
   * @returns {{safe: boolean, message?: string}}
   */
  checkSafety(query) {
    for (const pattern of this._unsafePatterns) {
      if (pattern.test(query)) {
        return {
          safe: false,
          message: 'I\'m unable to process that request. Please ask a different question.'
        };
      }
    }
    return { safe: true };
  }

  /**
   * D. Grounding guardrail
   * Verify answer is supported by retrieved context
   * @param {string} answer
   * @param {string} context
   * @returns {{grounded: boolean, confidence: number}}
   */
  checkGrounding(answer, context) {
    if (!answer || !context) {
      return { grounded: false, confidence: 0 };
    }

    // Check how many answer words appear in context
    const answerWords = answer.toLowerCase()
      .split(/\s+/)
      .filter(w => w.length > 3); // Skip small words

    const contextLower = context.toLowerCase();

    let matchedWords = 0;
    for (const word of answerWords) {
      if (contextLower.includes(word)) {
        matchedWords++;
      }
    }

    const confidence = answerWords.length > 0 ? matchedWords / answerWords.length : 0;

    return {
      grounded: confidence > 0.3, // At least 30% of content words grounded
      confidence
    };
  }

  /**
   * E. Citation guardrail
   * Validate that cited sources were actually retrieved
   * @param {Array} claimedSources
   * @param {Array} retrievedResults
   * @returns {{validSources: Array}}
   */
  validateCitations(claimedSources, retrievedResults) {
    if (!claimedSources || !Array.isArray(claimedSources)) {
      return { validSources: [] };
    }

    const retrievedIds = new Set(retrievedResults.map(r => r.chunk.id));

    const validSources = claimedSources.filter(src => {
      return retrievedIds.has(src.id);
    });

    return { validSources };
  }

  /**
   * F. Prompt injection defense
   * Check if text contains injection attempts
   * @param {string} text
   * @returns {{isInjection: boolean, pattern?: string}}
   */
  checkInjection(text) {
    for (const pattern of this._injectionPatterns) {
      if (pattern.test(text)) {
        return {
          isInjection: true,
          pattern: pattern.source
        };
      }
    }
    return { isInjection: false };
  }

  /**
   * G. Output guardrail
   * Validate the output structure
   * @param {object} output
   * @returns {{valid: boolean, errors: string[]}}
   */
  validateOutput(output) {
    const errors = [];

    if (!output) {
      errors.push('Output is null/undefined');
      return { valid: false, errors };
    }

    if (typeof output.answer !== 'string' || output.answer.trim() === '') {
      errors.push('Missing or empty answer');
    }

    if (typeof output.grounded !== 'boolean') {
      errors.push('Missing grounded boolean');
    }

    if (!Array.isArray(output.sources)) {
      errors.push('Missing sources array');
    } else {
      for (let i = 0; i < output.sources.length; i++) {
        const src = output.sources[i];
        if (!src.id) errors.push(`Source ${i} missing id`);
        if (!src.title) errors.push(`Source ${i} missing title`);
      }
    }

    return { valid: errors.length === 0, errors };
  }
}

module.exports = { Guardrails };
