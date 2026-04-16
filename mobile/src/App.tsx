import { useFonts } from 'expo-font';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { RootNavigator } from './navigation/RootNavigator';

export default function App() {
  const [fontsLoaded] = useFonts({
    'LXGWWenKaiScreen': require('./assets/fonts/LXGWWenKaiScreen.ttf'),
    // Android requires explicit weight-variant registrations.
    // Without these, fontWeight: 'bold' causes fallback to system font.
    'LXGWWenKaiScreen_bold': require('./assets/fonts/LXGWWenKaiScreen.ttf'),
    'LXGWWenKaiScreen_semibold': require('./assets/fonts/LXGWWenKaiScreen.ttf'),
    'LXGWWenKaiScreen_medium': require('./assets/fonts/LXGWWenKaiScreen.ttf'),
    'LXGWWenKaiScreen_light': require('./assets/fonts/LXGWWenKaiScreen.ttf'),
  });

  if (!fontsLoaded) {
    return null;
  }

  return (
    <SafeAreaProvider>
      <RootNavigator />
      <StatusBar style="dark" />
    </SafeAreaProvider>
  );
}


