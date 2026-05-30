import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './layout/Layout'
import ExecutiveOverview   from './pages/ExecutiveOverview'
import TrendsDashboard     from './pages/TrendsDashboard'
import TokenOpportunities  from './pages/TokenOpportunities'
import CEODecisionCenter   from './pages/CEODecisionCenter'
import SocialPerformance   from './pages/SocialPerformance'
import SocialDrafts        from './pages/SocialDrafts'
import BrandDashboard      from './pages/BrandDashboard'
import RiskDashboard       from './pages/RiskDashboard'
import ContractDashboard   from './pages/ContractDashboard'
import LaunchReadiness     from './pages/LaunchReadiness'
import AgentMonitor        from './pages/AgentMonitor'
import ReportsCenter       from './pages/ReportsCenter'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/"          element={<ExecutiveOverview />} />
          <Route path="/trends"    element={<TrendsDashboard />} />
          <Route path="/tokens"    element={<TokenOpportunities />} />
          <Route path="/ceo"       element={<CEODecisionCenter />} />
          <Route path="/social"    element={<SocialPerformance />} />
          <Route path="/drafts"    element={<SocialDrafts />} />
          <Route path="/brand"     element={<BrandDashboard />} />
          <Route path="/risk"      element={<RiskDashboard />} />
          <Route path="/contracts" element={<ContractDashboard />} />
          <Route path="/launch"    element={<LaunchReadiness />} />
          <Route path="/agents"    element={<AgentMonitor />} />
          <Route path="/reports"   element={<ReportsCenter />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
