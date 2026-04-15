/**
 * ToolGroup Component
 *
 * Collapsible tool call display for mobile.
 * - Default collapsed: shows tool call status summary
 * - Expanded: shows each tool's name, status, input/output
 * - Status icons: ✓ success, ✗ error, ○ in progress
 */

import React, { useState } from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { Wrench, ChevronDown, ChevronRight, ChevronUp, CheckCircle2, XCircle, RefreshCw } from 'lucide-react-native';
import { colors, spacing } from '../../../styles';
import type { ToolEvent } from '../../../types/chat';

interface ToolGroupProps {
  events: ToolEvent[];
}

/**
 * ToolGroup - Displays tool calls in collapsible format
 *
 * @param events - Array of ToolEvent objects
 */
export const ToolGroup: React.FC<ToolGroupProps> = ({ events }) => {
  const [expanded, setExpanded] = useState(false);

  const doneCount = events.filter((e) => e.status === 'END').length;
  const errorCount = events.filter((e) => e.status === 'ERROR').length;
  const totalCount = events.length;
  const allDone = doneCount + errorCount === totalCount && totalCount > 0;

  const getStatusIcon = () => {
    if (allDone) {
      if (errorCount > 0) return <XCircle size={14} color={colors.error} />;
      return <CheckCircle2 size={14} color={colors.success} />;
    }
    return <RefreshCw size={14} color={colors.accent} />;
  };

  const getToolStatusIcon = (status: ToolEvent['status']) => {
    switch (status) {
      case 'END':
        return <CheckCircle2 size={14} color={colors.success} />;
      case 'ERROR':
        return <XCircle size={14} color={colors.error} />;
      default:
        return <RefreshCw size={14} color={colors.accent} />;
    }
  };

  if (totalCount === 0) {
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
        <Wrench size={16} color={colors.accent} />
        <View style={styles.statusBadge}>
          {getStatusIcon()}
        </View>
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
          {events.map((event) => (
            <View key={event.id} style={styles.toolItem}>
              <View style={styles.toolHeader}>
                {getToolStatusIcon(event.status)}
                <Text style={[styles.toolName, { marginLeft: spacing[2] }]}>{event.name}</Text>
              </View>

              {/* Input section */}
              {event.input && Object.keys(event.input).length > 0 && (
                <View style={styles.toolSection}>
                  <View style={styles.codeBlock}>
                    <Text style={styles.codeText}>
                      {JSON.stringify(event.input, null, 2)}
                    </Text>
                  </View>
                </View>
              )}

              {/* Output section */}
              {event.output && Object.keys(event.output).length > 0 && (
                <View style={styles.toolSection}>
                  <View style={styles.codeBlock}>
                    <Text style={styles.codeText}>
                      {JSON.stringify(event.output, null, 2)}
                    </Text>
                  </View>
                </View>
              )}

              {/* Error section */}
              {event.error && (
                <View style={styles.toolSection}>
                  <View style={[styles.codeBlock, styles.errorBlock]}>
                    <Text style={[styles.codeText, styles.errorText]}>
                      {event.error}
                    </Text>
                  </View>
                </View>
              )}
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

const styles = StyleSheet.create({
  container: {
    marginVertical: spacing[2],
    marginHorizontal: spacing[4],
    backgroundColor: colors.toolBg,
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
  headerText: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
    marginLeft: spacing[2],
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    marginLeft: spacing[2],
    flex: 1,
  },
  iconDone: {
    fontSize: 12,
    color: colors.success,
    marginRight: spacing[1],
  },
  iconRunning: {
    fontSize: 12,
    color: colors.accent,
    marginRight: spacing[1],
  },
  statusText: {
    fontSize: 13,
    color: colors.textLight,
  },
  toggleIcon: {
    marginLeft: 'auto',
  },
  expandHint: {
    paddingHorizontal: spacing[3],
    paddingBottom: spacing[2],
  },
  expandHintText: {
    fontSize: 13,
    color: colors.accent,
  },
  content: {
    paddingHorizontal: spacing[3],
    paddingBottom: spacing[3],
  },
  toolItem: {
    marginBottom: spacing[3],
    backgroundColor: colors.backgroundCard,
    borderRadius: 8,
    padding: spacing[2],
    borderWidth: 1,
    borderColor: colors.border,
  },
  toolHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: spacing[1],
  },
  statusIconDone: {
    fontSize: 14,
    color: colors.success,
    marginRight: spacing[1],
  },
  statusIconError: {
    fontSize: 14,
    color: colors.error,
    marginRight: spacing[1],
  },
  statusIconRunning: {
    fontSize: 14,
    color: colors.accent,
    marginRight: spacing[1],
  },
  toolName: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
    flex: 1,
  },
  toolStatusText: {
    fontSize: 12,
    color: colors.textLight,
  },
  toolStatusSuccess: {
    color: colors.success,
  },
  toolStatusError: {
    color: colors.error,
  },
  toolSection: {
    marginTop: spacing[2],
  },
  sectionLabel: {
    fontSize: 12,
    color: colors.textMuted,
    marginBottom: spacing[1],
  },
  codeBlock: {
    backgroundColor: colors.moodBg,
    borderRadius: 6,
    padding: spacing[2],
    borderWidth: 1,
    borderColor: colors.border,
  },
  codeText: {
    fontSize: 12,
    fontFamily: 'monospace',
    color: colors.text,
  },
  errorBlock: {
    backgroundColor: colors.errorBg,
    borderColor: colors.error,
  },
  errorText: {
    color: colors.error,
  },
  collapseButton: {
    alignSelf: 'center',
    paddingHorizontal: spacing[4],
    paddingVertical: spacing[2],
    marginTop: spacing[2],
  },
});

export default ToolGroup;
