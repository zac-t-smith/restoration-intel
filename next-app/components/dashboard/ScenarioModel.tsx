/**
 * Scenario Model (What-If Panel) Component
 * 
 * Allows users to simulate different business scenarios by adjusting key parameters
 * and visualize the projected 18-month Revenue, Gross Profit, and Cash
 */

'use client';

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Slider } from '@/components/ui/slider';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';

// Dynamically import Plotly to avoid SSR issues
const Plot = dynamic(() => import('react-plotly.js'), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[350px] flex items-center justify-center">
      <Skeleton className="w-full h-full" />
    </div>
  )
});

interface BaselineMetrics {
  currentCash: number;
  avgProjectValue: number;
  avgProjectDuration: number;
  grossProfitMargin: number;
  monthlyRevenue: number;
  closeRate: number;
  estimatedCrewCount: number;
  utilization: number;
}

interface SimulationResult {
  months: string[];
  revenue: number[];
  grossProfit: number[];
  cash: number[];
  projectsPerMonth: number[];
  leadsPerMonth: number[];
}

export default function ScenarioModel() {
  // Input parameters
  const [crewCount, setCrewCount] = useState<number>(5);
  const [utilisation, setUtilisation] = useState<number>(75);
  const [closeRate, setCloseRate] = useState<number>(30);
  const [priceUplift, setPriceUplift] = useState<number>(0);
  
  // Simulation results
  const [results, setResults] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [baselineMetrics, setBaselineMetrics] = useState<BaselineMetrics>({
    currentCash: 250000,
    avgProjectValue: 15000,
    avgProjectDuration: 14,
    grossProfitMargin: 0.35,
    monthlyRevenue: 120000,
    closeRate: 0.25,
    estimatedCrewCount: 4,
    utilization: 0.7
  });
  
  // Format currency values
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0
    }).format(value);
  };
  
  // Format percentage values
  const formatPercent = (value: number) => {
    return `${value}%`;
  };
  
  // Run simulation when inputs change
  useEffect(() => {
    runSimulation();
  }, [crewCount, utilisation, closeRate, priceUplift]);
  
  // Fetch baseline metrics from API (simulated)
  useEffect(() => {
    const fetchBaselineMetrics = async () => {
      // In a real implementation, this would fetch from the API
      // Using simulated data for now
      setBaselineMetrics({
        currentCash: 250000,
        avgProjectValue: 15000,
        avgProjectDuration: 14,
        grossProfitMargin: 0.35,
        monthlyRevenue: 120000,
        closeRate: 0.25,
        estimatedCrewCount: 4,
        utilization: 0.7
      });
    };
    
    fetchBaselineMetrics();
  }, []);
  
  // Run the simulation with current parameters
  const runSimulation = () => {
    setLoading(true);
    
    // Simulate API call delay
    setTimeout(() => {
      // Calculate the simulation results
      const months = [];
      const revenue = [];
      const grossProfit = [];
      const cash = [];
      const projectsPerMonth = [];
      const leadsPerMonth = [];
      
      // Start with current cash
      let currentCash = baselineMetrics.currentCash;
      
      // Calculate capacity based on crew count and utilization
      const crewCapacity = crewCount * (utilisation / 100);
      
      // Calculate projects per month based on capacity
      const baseProjectsPerMonth = crewCapacity * 2; // Assuming each crew can handle 2 projects per month at 100% utilization
      
      // Calculate adjusted price based on price uplift
      const adjustedPrice = baselineMetrics.avgProjectValue * (1 + priceUplift / 100);
      
      // Calculate adjusted gross profit margin (price uplift increases margin)
      const adjustedMargin = baselineMetrics.grossProfitMargin * (1 + (priceUplift / 2) / 100);
      
      // Calculate adjusted close rate
      const adjustedCloseRate = closeRate / 100;
      
      // Generate 18 months of data
      for (let i = 0; i < 18; i++) {
        // Calculate month
        const date = new Date();
        date.setMonth(date.getMonth() + i);
        months.push(date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }));
        
        // Calculate number of projects with some randomness
        const randomFactor = 0.9 + Math.random() * 0.2; // Between 0.9 and 1.1
        const monthlyProjects = Math.round(baseProjectsPerMonth * randomFactor);
        projectsPerMonth.push(monthlyProjects);
        
        // Calculate required leads based on close rate
        const requiredLeads = Math.round(monthlyProjects / adjustedCloseRate);
        leadsPerMonth.push(requiredLeads);
        
        // Calculate monthly revenue
        const monthlyRevenue = monthlyProjects * adjustedPrice;
        revenue.push(monthlyRevenue);
        
        // Calculate monthly gross profit
        const monthlyGrossProfit = monthlyRevenue * adjustedMargin;
        grossProfit.push(monthlyGrossProfit);
        
        // Calculate cash (simplified model)
        // Assume 70% of revenue is collected in the current month, 20% in the next month, 10% in the third month
        // Assume expenses are 70% of revenue minus gross profit, paid in the current month
        const expenses = monthlyRevenue - monthlyGrossProfit;
        
        // Calculate collections (simplified)
        const collections = monthlyRevenue * 0.7; // 70% collected in current month
        
        // Calculate payments (simplified)
        const payments = expenses * 0.9; // 90% paid in current month
        
        // Update cash balance
        currentCash = currentCash + collections - payments;
        cash.push(currentCash);
      }
      
      setResults({
        months,
        revenue,
        grossProfit,
        cash,
        projectsPerMonth,
        leadsPerMonth
      });
      
      setLoading(false);
    }, 500);
  };
  
  // Reset to defaults
  const resetToDefaults = () => {
    setCrewCount(5);
    setUtilisation(75);
    setCloseRate(30);
    setPriceUplift(0);
  };
  
  // Download simulation results as CSV
  const downloadCSV = () => {
    if (!results) return;
    
    // Create CSV content
    let csvContent = "Month,Revenue,Gross Profit,Cash Balance,Projects,Leads Required\n";
    
    for (let i = 0; i < results.months.length; i++) {
      csvContent += `${results.months[i]},${results.revenue[i]},${results.grossProfit[i]},${results.cash[i]},${results.projectsPerMonth[i]},${results.leadsPerMonth[i]}\n`;
    }
    
    // Create and download the file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'scenario_simulation.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-bold">Scenario Model (What-If Analysis)</h2>
        <Button 
          onClick={resetToDefaults} 
          variant="outline"
          size="sm"
        >
          Reset to Defaults
        </Button>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left column: Input parameters */}
        <Card>
          <CardHeader>
            <CardTitle>Scenario Parameters</CardTitle>
            <CardDescription>
              Adjust parameters to simulate different business scenarios
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Crew Count */}
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label htmlFor="crew-count">Crew Count</Label>
                <span className="text-sm font-medium">{crewCount}</span>
              </div>
              <div className="flex space-x-2">
                <Slider
                  id="crew-count"
                  min={1}
                  max={20}
                  step={1}
                  value={[crewCount]}
                  onValueChange={(value) => setCrewCount(value[0])}
                  className="flex-1"
                />
                <Input
                  type="number"
                  value={crewCount}
                  onChange={(e) => setCrewCount(Number(e.target.value))}
                  className="w-16"
                />
              </div>
              <p className="text-xs text-gray-500">
                Number of crews available for projects (current: {baselineMetrics.estimatedCrewCount})
              </p>
            </div>
            
            {/* Utilisation */}
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label htmlFor="utilisation">Utilisation %</Label>
                <span className="text-sm font-medium">{utilisation}%</span>
              </div>
              <div className="flex space-x-2">
                <Slider
                  id="utilisation"
                  min={10}
                  max={100}
                  step={1}
                  value={[utilisation]}
                  onValueChange={(value) => setUtilisation(value[0])}
                  className="flex-1"
                />
                <Input
                  type="number"
                  value={utilisation}
                  onChange={(e) => setUtilisation(Number(e.target.value))}
                  className="w-16"
                />
              </div>
              <p className="text-xs text-gray-500">
                Percentage of crew time utilized on billable work (current: {baselineMetrics.utilization * 100}%)
              </p>
            </div>
            
            {/* Close Rate */}
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label htmlFor="close-rate">Close Rate %</Label>
                <span className="text-sm font-medium">{closeRate}%</span>
              </div>
              <div className="flex space-x-2">
                <Slider
                  id="close-rate"
                  min={5}
                  max={80}
                  step={1}
                  value={[closeRate]}
                  onValueChange={(value) => setCloseRate(value[0])}
                  className="flex-1"
                />
                <Input
                  type="number"
                  value={closeRate}
                  onChange={(e) => setCloseRate(Number(e.target.value))}
                  className="w-16"
                />
              </div>
              <p className="text-xs text-gray-500">
                Percentage of leads that convert to projects (current: {baselineMetrics.closeRate * 100}%)
              </p>
            </div>
            
            {/* Price Uplift */}
            <div className="space-y-2">
              <div className="flex justify-between">
                <Label htmlFor="price-uplift">Price Uplift %</Label>
                <span className="text-sm font-medium">{priceUplift > 0 ? '+' : ''}{priceUplift}%</span>
              </div>
              <div className="flex space-x-2">
                <Slider
                  id="price-uplift"
                  min={-20}
                  max={30}
                  step={1}
                  value={[priceUplift]}
                  onValueChange={(value) => setPriceUplift(value[0])}
                  className="flex-1"
                />
                <Input
                  type="number"
                  value={priceUplift}
                  onChange={(e) => setPriceUplift(Number(e.target.value))}
                  className="w-16"
                />
              </div>
              <p className="text-xs text-gray-500">
                Percentage increase/decrease in project pricing (avg job: {formatCurrency(baselineMetrics.avgProjectValue)})
              </p>
            </div>
            
            {/* Summary Metrics */}
            <div className="pt-4 mt-4 border-t border-gray-200">
              <h3 className="text-sm font-medium mb-2">Scenario Summary Metrics</h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="bg-gray-50 p-3 rounded-md">
                  <div className="text-xs text-gray-500">Monthly Revenue</div>
                  <div className="text-lg font-semibold">
                    {results ? formatCurrency(results.revenue[0]) : '-'}
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded-md">
                  <div className="text-xs text-gray-500">Monthly GP</div>
                  <div className="text-lg font-semibold">
                    {results ? formatCurrency(results.grossProfit[0]) : '-'}
                  </div>
                </div>
                <div className="bg-gray-50 p-3 rounded-md">
                  <div className="text-xs text-gray-500">Cash (Month 18)</div>
                  <div className="text-lg font-semibold">
                    {results ? formatCurrency(results.cash[17]) : '-'}
                  </div>
                </div>
              </div>
              <Button 
                onClick={downloadCSV}
                variant="outline"
                size="sm"
                className="mt-4 w-full"
                disabled={!results}
              >
                Download Full Results (CSV)
              </Button>
            </div>
          </CardContent>
        </Card>
        
        {/* Right column: Visualization */}
        <Card>
          <CardHeader>
            <CardTitle>18-Month Projection</CardTitle>
            <CardDescription>
              Visualize Revenue, Gross Profit, and Cash based on scenario parameters
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="w-full h-[350px] flex items-center justify-center">
                <Skeleton className="w-full h-full" />
              </div>
            ) : results ? (
              <div className="space-y-6">
                {/* Projection Chart */}
                <Plot
                  data={[
                    {
                      x: results.months,
                      y: results.revenue,
                      type: 'scatter',
                      mode: 'lines',
                      name: 'Revenue',
                      line: {
                        color: 'rgba(59, 130, 246, 0.8)', // blue-500
                        width: 2
                      } as any
                    },
                    {
                      x: results.months,
                      y: results.grossProfit,
                      type: 'scatter',
                      mode: 'lines',
                      name: 'Gross Profit',
                      line: {
                        color: 'rgba(16, 185, 129, 0.8)', // green-500
                        width: 2
                      } as any
                    },
                    {
                      x: results.months,
                      y: results.cash,
                      type: 'scatter',
                      mode: 'lines',
                      name: 'Cash',
                      line: {
                        color: 'rgba(245, 158, 11, 0.8)', // amber-500
                        width: 3
                      } as any
                    }
                  ]}
                  layout={{
                    height: 350,
                    margin: {
                      l: 50,
                      r: 20,
                      t: 10,
                      b: 40
                    },
                    legend: {
                      orientation: 'h',
                      y: -0.2
                    },
                    yaxis: {
                      title: 'Amount ($)',
                      tickformat: '$,.0f'
                    },
                    hovermode: 'x unified',
                    autosize: true
                  } as any}
                  config={{
                    responsive: true,
                    displayModeBar: false
                  }}
                  className="w-full"
                />
                
                {/* Monthly Details Table (first 6 months) */}
                <div>
                  <h3 className="text-sm font-medium mb-2">Monthly Breakdown (First 6 Months)</h3>
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead>Month</TableHead>
                          <TableHead>Revenue</TableHead>
                          <TableHead>Gross Profit</TableHead>
                          <TableHead>Cash</TableHead>
                          <TableHead>Projects</TableHead>
                          <TableHead>Leads</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {results.months.slice(0, 6).map((month, i) => (
                          <TableRow key={i}>
                            <TableCell>{month}</TableCell>
                            <TableCell>{formatCurrency(results.revenue[i])}</TableCell>
                            <TableCell>{formatCurrency(results.grossProfit[i])}</TableCell>
                            <TableCell>{formatCurrency(results.cash[i])}</TableCell>
                            <TableCell>{results.projectsPerMonth[i]}</TableCell>
                            <TableCell>{results.leadsPerMonth[i]}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-500">
                Adjust parameters to see projections
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}