import { Tabs } from "expo-router";

export default function TabsLayout() {
  return (
    <Tabs screenOptions={{ headerShown: true }}>
      <Tabs.Screen
        name="index"
        options={{ title: "Projects", tabBarLabel: "Projects" }}
      />
      <Tabs.Screen
        name="editor"
        options={{ title: "Editor", tabBarLabel: "Write" }}
      />
      <Tabs.Screen
        name="project/[id]"
        options={{ href: null }}
      />
      <Tabs.Screen
        name="book/[projectId]/[bookId]"
        options={{ href: null }}
      />
      <Tabs.Screen
        name="editor/[projectId]/[bookId]/[chapterId]"
        options={{ href: null, title: "Editor" }}
      />
      <Tabs.Screen
        name="settings"
        options={{ title: "Settings", tabBarLabel: "Settings" }}
      />
    </Tabs>
  );
}
