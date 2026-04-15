/**
 * ThinkingBlock Component
 *
 * Collapsible AI thinking process display.
 * - Default collapsed: shows "🧠 AI 思考过程 (N步)" with expand button
 * - Expanded: shows all thinking steps
 * - Toggle all steps at once
 */

import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Brain, ChevronDown, ChevronRight, ChevronUp } from 'lucide-react-native';
import ReactMarkdown from 'react-native-markdown-display';
import { colors, spacing } from '../../../styles';

interface ThinkingBlockProps {
  thinking: string[];
}

/**
 * ThinkingBlock - Displays AI thinking process in collapsible format
 *
 * @param thinking - Array of thinking step strings
 */
export const ThinkingBlock: React.FC<ThinkingBlockProps> = ({ thinking }) => {
  const [expanded, setExpanded] = useState(false);

  if (thinking.length === 0) {
    return null;
  }

  const toggleExpand = () => {
    setExpanded((prev) => !prev);
  };

  return (
    <View style={styles.container}>
      <TouchableOpacity
        style={styles.header}
        onPress={toggleExpand}
        activeOpacity={0.7}
      >
        <Brain size={18} color={colors.accent} />
        <Text style={styles.stepCount}>({thinking.length})</Text>
        <View style={styles.toggleIcon}>
          {expanded ? (
            <ChevronDown size={18} color={colors.textLight} />
          ) : (
            <ChevronRight size={18} color={colors.textLight} />
          )}
        </View>
      </TouchableOpacity>

      {/* Content - shown when expanded */}
      {expanded && (
        <View style={styles.content}>
          {thinking.map((thought, index) => (
            <View key={index} style={styles.thoughtItem}>
              <View style={styles.thoughtHeader}>
                <View style={styles.stepIndicator}>
                  <Text style={styles.stepNumber}>{index + 1}</Text>
                </View>
              </View>
              <View style={styles.thoughtBody}>
                <ReactMarkdown style={markdownStyles}>{thought}</ReactMarkdown>
              </View>
            </View>
          ))}

          {/* Collapse button */}
          <TouchableOpacity
            style={styles.collapseButton}
            onPress={toggleExpand}
            activeOpacity={0.7}
          >
            <ChevronUp size={20} color={colors.textLight} />
          </TouchableOpacity>
        </View>
      )}
    </View>
  );
};

// Markdown styles for thinking content
const markdownStyles = StyleSheet.create({
  body: {
    color: colors.assistantText,
    fontSize: 14,
    lineHeight: 20,
  },
  paragraph: {
    marginVertical: 2,
  },
  code_inline: {
    backgroundColor: colors.moodBg,
    color: colors.accent,
    paddingHorizontal: 4,
    paddingVertical: 2,
    borderRadius: 4,
    fontFamily: 'monospace',
    fontSize: 12,
  },
  code_block: {
    backgroundColor: colors.moodBg,
    padding: 8,
    borderRadius: 8,
    marginVertical: 4,
  },
  fence: {
    backgroundColor: colors.moodBg,
    padding: 8,
    borderRadius: 8,
    marginVertical: 4,
  },
  link: {
    color: colors.accent,
  },
  strong: {
    fontWeight: 'bold',
  },
  em: {
    fontStyle: 'italic',
  },
});

const styles = StyleSheet.create({
  container: {
    marginVertical: spacing[2],
    marginHorizontal: spacing[4],
    backgroundColor: colors.moodBg,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.moodBorder,
    overflow: 'hidden',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: spacing[3],
    paddingVertical: spacing[2],
  },
  stepCount: {
    fontSize: 14,
    color: colors.textLight,
    marginLeft: spacing[1],
  },
  toggleIcon: {
    marginLeft: 'auto',
  },
  content: {
    paddingHorizontal: spacing[3],
    paddingBottom: spacing[3],
  },
  thoughtItem: {
    marginBottom: spacing[3],
  },
  thoughtHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing[1],
  },
  stepIndicator: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: colors.accent,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: spacing[2],
  },
  stepNumber: {
    fontSize: 11,
    fontWeight: 'bold',
    color: colors.backgroundCard,
  },
  thoughtBody: {
    marginLeft: spacing[6],
    paddingLeft: spacing[3],
    borderLeftWidth: 2,
    borderLeftColor: colors.border,
  },
  collapseButton: {
    alignSelf: 'center',
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[2],
    marginTop: spacing[2],
  },
});

export default ThinkingBlock;
