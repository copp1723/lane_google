# Dashboard Components Dependencies

## NPM Packages Required

The copied dashboard components require the following npm packages:

```bash
# Required for chart visualization in StatusDistributionChart.tsx
npm install react-chartjs-2 chart.js

# Required for date formatting in task-widget.tsx
npm install date-fns

# Required for styling utilities
npm install clsx tailwind-merge

# Required for icons
npm install lucide-react
```

## UI Components Required

These components depend on shadcn/ui components:
- Card (CardContent, CardHeader, CardTitle)
- Button
- Badge

To install these components using shadcn/ui CLI:
```bash
npx shadcn-ui@latest add card
npx shadcn-ui@latest add button
npx shadcn-ui@latest add badge
```

## Component Usage

### 1. PackageUsageProgress.tsx
Shows monthly package usage with progress bars.
```typescript
<PackageUsageProgress usageData={{
  pages: 5,
  blogs: 3,
  gbpPosts: 2,
  improvements: 1
}} />
```

### 2. RecentActivityTimeline.tsx
Displays recent activities in a timeline format.
```typescript
<RecentActivityTimeline activities={[
  { id: '1', description: 'Task created', time: '2 hours ago' },
  { id: '2', description: 'Status changed to COMPLETED', time: '1 hour ago' }
]} />
```

### 3. StatusDistributionChart.tsx
Shows a doughnut chart of status distribution.
```typescript
<StatusDistributionChart statusCounts={{
  PENDING: 5,
  IN_PROGRESS: 3,
  COMPLETED: 10,
  CANCELLED: 1
}} />
```

### 4. UpcomingTasks.tsx
Lists upcoming tasks with deadline information.
```typescript
<UpcomingTasks tasks={[
  {
    id: '1',
    title: 'Review campaign content',
    dueDate: '2025-07-10',
    daysRemaining: 6,
    status: 'IN_PROGRESS'
  }
]} />
```

### 5. TaskWidget
A comprehensive task widget with advanced features.
```typescript
<TaskWidget 
  tasks={tasks}
  title="Campaign Tasks"
  showViewAll={true}
  maxTasks={5}
/>
```

## Import Path Updates

All components use `@/` imports which should be configured in your tsconfig.json:
```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
```