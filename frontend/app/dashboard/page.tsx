import { DashboardHome } from '@/components/dashboard-home'
import { DashboardShell } from '@/components/dashboard-shell'

export default function DashboardPage() {
  return (
    <DashboardShell>
      <DashboardHome />
    </DashboardShell>
  )
}
