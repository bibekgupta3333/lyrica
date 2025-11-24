import React from 'react';
import {
  StyleSheet,
  Text,
  View,
  ScrollView,
  TouchableOpacity,
  useColorScheme,
} from 'react-native';

const HomeScreen = ({navigation}: any) => {
  const isDarkMode = useColorScheme() === 'dark';

  const styles = createStyles(isDarkMode);

  return (
    <ScrollView style={styles.container}>
      <View style={styles.content}>
        {/* Hero Section */}
        <View style={styles.hero}>
          <Text style={styles.emoji}>🎵</Text>
          <Text style={styles.title}>Lyrica</Text>
          <Text style={styles.subtitle}>Agentic Song Lyrics Generator</Text>
          <Text style={styles.description}>
            Generate creative song lyrics using AI agents powered by RAG and
            local LLMs
          </Text>
        </View>

        {/* Features */}
        <View style={styles.featuresContainer}>
          <FeatureCard
            icon="🤖"
            title="AI Agents"
            description="Multi-agent system using LangGraph"
            isDarkMode={isDarkMode}
          />
          <FeatureCard
            icon="🔍"
            title="RAG System"
            description="ChromaDB vector store integration"
            isDarkMode={isDarkMode}
          />
          <FeatureCard
            icon="💻"
            title="Local LLM"
            description="Powered by Ollama (Llama 3 / Mistral)"
            isDarkMode={isDarkMode}
          />
          <FeatureCard
            icon="⚡"
            title="Real-time"
            description="WebSocket streaming generation"
            isDarkMode={isDarkMode}
          />
        </View>

        {/* CTA Button */}
        <TouchableOpacity
          style={styles.button}
          onPress={() => {
            // TODO: Navigate to generate screen
            console.log('Generate lyrics - Coming soon!');
          }}>
          <Text style={styles.buttonText}>Generate Lyrics</Text>
        </TouchableOpacity>

        {/* Status */}
        <View style={styles.statusContainer}>
          <Text style={styles.statusTitle}>Backend Status</Text>
          <View style={styles.statusRow}>
            <View style={styles.statusDot} />
            <Text style={styles.statusText}>API: localhost:8000</Text>
          </View>
        </View>

        {/* Tech Stack */}
        <View style={styles.techStack}>
          <Text style={styles.techTitle}>Built with</Text>
          <View style={styles.techTags}>
            {['FastAPI', 'React Native', 'LangGraph', 'ChromaDB', 'PostgreSQL'].map(
              tech => (
                <View key={tech} style={styles.techTag}>
                  <Text style={styles.techTagText}>{tech}</Text>
                </View>
              ),
            )}
          </View>
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>
            Built with ❤️ using React Native
          </Text>
        </View>
      </View>
    </ScrollView>
  );
};

const FeatureCard = ({
  icon,
  title,
  description,
  isDarkMode,
}: {
  icon: string;
  title: string;
  description: string;
  isDarkMode: boolean;
}) => {
  return (
    <View
      style={[
        styles.featureCard,
        {backgroundColor: isDarkMode ? '#2a2a2a' : '#ffffff'},
      ]}>
      <Text style={styles.featureIcon}>{icon}</Text>
      <Text
        style={[
          styles.featureTitle,
          {color: isDarkMode ? '#ffffff' : '#000000'},
        ]}>
        {title}
      </Text>
      <Text
        style={[
          styles.featureDescription,
          {color: isDarkMode ? '#cccccc' : '#666666'},
        ]}>
        {description}
      </Text>
    </View>
  );
};

const createStyles = (isDarkMode: boolean) =>
  StyleSheet.create({
    container: {
      flex: 1,
      backgroundColor: isDarkMode ? '#1a1a1a' : '#f5f5f5',
    },
    content: {
      padding: 20,
    },
    hero: {
      alignItems: 'center',
      marginBottom: 30,
      paddingVertical: 30,
    },
    emoji: {
      fontSize: 60,
      marginBottom: 10,
    },
    title: {
      fontSize: 42,
      fontWeight: 'bold',
      color: isDarkMode ? '#ffffff' : '#000000',
      marginBottom: 10,
    },
    subtitle: {
      fontSize: 20,
      color: isDarkMode ? '#cccccc' : '#666666',
      marginBottom: 15,
      textAlign: 'center',
    },
    description: {
      fontSize: 16,
      color: isDarkMode ? '#999999' : '#888888',
      textAlign: 'center',
      paddingHorizontal: 20,
      lineHeight: 24,
    },
    featuresContainer: {
      marginBottom: 30,
    },
    featureCard: {
      padding: 20,
      borderRadius: 12,
      marginBottom: 15,
      shadowColor: '#000',
      shadowOffset: {width: 0, height: 2},
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 3,
    },
    featureIcon: {
      fontSize: 40,
      marginBottom: 10,
    },
    featureTitle: {
      fontSize: 18,
      fontWeight: '600',
      marginBottom: 8,
    },
    featureDescription: {
      fontSize: 14,
      lineHeight: 20,
    },
    button: {
      backgroundColor: '#6366f1',
      paddingVertical: 16,
      paddingHorizontal: 32,
      borderRadius: 12,
      alignItems: 'center',
      marginBottom: 30,
      shadowColor: '#6366f1',
      shadowOffset: {width: 0, height: 4},
      shadowOpacity: 0.3,
      shadowRadius: 8,
      elevation: 5,
    },
    buttonText: {
      color: '#ffffff',
      fontSize: 18,
      fontWeight: '700',
    },
    statusContainer: {
      padding: 20,
      backgroundColor: isDarkMode ? '#2a2a2a' : '#ffffff',
      borderRadius: 12,
      marginBottom: 20,
    },
    statusTitle: {
      fontSize: 16,
      fontWeight: '600',
      color: isDarkMode ? '#ffffff' : '#000000',
      marginBottom: 12,
    },
    statusRow: {
      flexDirection: 'row',
      alignItems: 'center',
    },
    statusDot: {
      width: 10,
      height: 10,
      borderRadius: 5,
      backgroundColor: '#22c55e',
      marginRight: 10,
    },
    statusText: {
      fontSize: 14,
      color: isDarkMode ? '#cccccc' : '#666666',
    },
    techStack: {
      marginBottom: 30,
    },
    techTitle: {
      fontSize: 14,
      color: isDarkMode ? '#999999' : '#666666',
      textAlign: 'center',
      marginBottom: 12,
    },
    techTags: {
      flexDirection: 'row',
      flexWrap: 'wrap',
      justifyContent: 'center',
      gap: 8,
    },
    techTag: {
      backgroundColor: isDarkMode ? '#2a2a2a' : '#ffffff',
      paddingVertical: 8,
      paddingHorizontal: 16,
      borderRadius: 20,
      borderWidth: 1,
      borderColor: isDarkMode ? '#444444' : '#e5e5e5',
    },
    techTagText: {
      fontSize: 12,
      color: isDarkMode ? '#cccccc' : '#666666',
    },
    footer: {
      paddingVertical: 20,
      alignItems: 'center',
    },
    footerText: {
      fontSize: 12,
      color: isDarkMode ? '#666666' : '#999999',
    },
  });

const styles = StyleSheet.create({
  // Common styles that don't change
  featureCard: {},
  featureIcon: {},
  featureTitle: {},
  featureDescription: {},
  button: {},
  buttonText: {},
  statusContainer: {},
  statusTitle: {},
  statusRow: {},
  statusDot: {},
  statusText: {},
  techStack: {},
  techTitle: {},
  techTags: {},
  techTag: {},
  techTagText: {},
  footer: {},
  footerText: {},
  container: {},
  content: {},
  hero: {},
  emoji: {},
  title: {},
  subtitle: {},
  description: {},
  featuresContainer: {},
});

export default HomeScreen;

