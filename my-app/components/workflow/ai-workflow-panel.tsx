"use client";

import { useState, useEffect } from "react";
import {
  Brain,
  AlertTriangle,
  Lightbulb,
  TrendingUp,
  RefreshCw,
  ChevronRight,
  Clock,
  Target,
  AlertCircle,
  CheckCircle2,
  ArrowUpRight,
  ArrowDownRight,
  Minus,
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  AIWorkflowAnalysis,
  AIWorkflowInsight,
  AIWorkflowHealth,
  AIPriorityRecommendation,
  AITimelinePrediction,
} from "@/lib/types";
import {
  getAIWorkflowAnalysis,
  getWorkflowHealth,
  getAIPriorityRecommendations,
} from "@/lib/api";
import { toast } from "sonner";

interface AIWorkflowPanelProps {
  eventId: string;
  className?: string;
}

const insightIcons = {
  warning: AlertTriangle,
  suggestion: Lightbulb,
  tip: TrendingUp,
  prediction: Brain,
};

const insightColors = {
  warning: {
    bg: "bg-destructive/10",
    border: "border-destructive/30",
    text: "text-destructive",
    icon: "text-destructive",
  },
  suggestion: {
    bg: "bg-primary/10",
    border: "border-primary/30",
    text: "text-primary",
    icon: "text-primary",
  },
  tip: {
    bg: "bg-secondary/50",
    border: "border-border",
    text: "text-muted-foreground",
    icon: "text-muted-foreground",
  },
  prediction: {
    bg: "bg-blue-500/10",
    border: "border-blue-500/30",
    text: "text-blue-500",
    icon: "text-blue-500",
  },
};

const impactBadges = {
  critical: {
    bg: "bg-red-500/20",
    text: "text-red-400",
    label: "Critical",
  },
  high: {
    bg: "bg-orange-500/20",
    text: "text-orange-400",
    label: "High",
  },
  medium: {
    bg: "bg-yellow-500/20",
    text: "text-yellow-400",
    label: "Medium",
  },
  low: {
    bg: "bg-green-500/20",
    text: "text-green-400",
    label: "Low",
  },
};

const healthColors = {
  excellent: {
    bg: "bg-gradient-to-r from-emerald-500 to-green-500",
    text: "text-emerald-600",
    label: "Excellent",
  },
  good: {
    bg: "bg-gradient-to-r from-blue-500 to-cyan-500",
    text: "text-blue-600",
    label: "Good",
  },
  needs_attention: {
    bg: "bg-gradient-to-r from-yellow-500 to-orange-500",
    text: "text-yellow-600",
    label: "Needs Attention",
  },
  critical: {
    bg: "bg-gradient-to-r from-red-500 to-pink-500",
    text: "text-red-600",
    label: "Critical",
  },
};

const riskColors = {
  low: {
    bg: "bg-green-500/20",
    text: "text-green-400",
    icon: CheckCircle2,
  },
  medium: {
    bg: "bg-yellow-500/20",
    text: "text-yellow-400",
    icon: AlertCircle,
  },
  high: {
    bg: "bg-red-500/20",
    text: "text-red-400",
    icon: AlertTriangle,
  },
  unknown: {
    bg: "bg-gray-500/20",
    text: "text-gray-400",
    icon: Minus,
  },
};

function InsightCard({
  insight,
  onClick,
}: {
  insight: AIWorkflowInsight;
  onClick?: () => void;
}) {
  const Icon = insightIcons[insight.type] || Brain;
  const colors = insightColors[insight.type];
  const impactBadge = impactBadges[insight.impact];

  return (
    <div
      className={cn(
        "rounded-lg border p-4 transition-all duration-200 cursor-pointer",
        colors.bg,
        colors.border,
        onClick && "hover:shadow-md"
      )}
      onClick={onClick}
    >
      <div className="flex items-start gap-3">
        <div
          className={cn(
            "flex h-8 w-8 shrink-0 items-center justify-center rounded-full",
            colors.bg
          )}
        >
          <Icon className={cn("h-4 w-4", colors.icon)} />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between gap-2 mb-1">
            <h4 className={cn("font-medium text-sm truncate", colors.text)}>
              {insight.title}
            </h4>
            <span
              className={cn(
                "text-xs px-2 py-0.5 rounded-full shrink-0",
                impactBadge.bg,
                impactBadge.text
              )}
            >
              {impactBadge.label}
            </span>
          </div>
          <p className="text-sm text-muted-foreground line-clamp-2">
            {insight.description}
          </p>
          {insight.recommendation && (
            <div
              className={cn(
                "mt-2 text-xs px-2 py-1 rounded",
                "bg-background/50 text-muted-foreground"
              )}
            >
              💡 {insight.recommendation}
            </div>
          )}
        </div>
        {onClick && (
          <ChevronRight className="h-4 w-4 text-muted-foreground shrink-0" />
        )}
      </div>
    </div>
  );
}

function PriorityRecommendationCard({
  recommendation,
}: {
  recommendation: AIPriorityRecommendation;
}) {
  const priorityChange =
    recommendation.suggestedPriority !== recommendation.currentPriority;

  return (
    <div className="rounded-lg border border-border bg-card p-3 transition-all hover:shadow-sm">
      <div className="flex items-center justify-between gap-2 mb-2">
        <h5 className="font-medium text-sm text-card-foreground truncate">
          {recommendation.taskTitle}
        </h5>
        {priorityChange && (
          <span className="flex items-center gap-1 text-xs text-primary shrink-0">
            {recommendation.currentPriority &&
              recommendation.suggestedPriority === "high" && (
                <ArrowUpRight className="h-3 w-3" />
              )}
            {recommendation.currentPriority &&
              recommendation.suggestedPriority === "medium" && (
                <ArrowDownRight className="h-3 w-3" />
              )}
            {recommendation.currentPriority} → {recommendation.suggestedPriority}
          </span>
        )}
      </div>
      <p className="text-xs text-muted-foreground mb-2">
        {recommendation.reason}
      </p>
      <div className="flex flex-wrap gap-1">
        {recommendation.factors.slice(0, 3).map((factor, index) => (
          <span
            key={index}
            className="text-xs px-2 py-0.5 rounded-full bg-secondary text-secondary-foreground"
          >
            {factor}
          </span>
        ))}
      </div>
    </div>
  );
}

function HealthScoreCard({ health }: { health: AIWorkflowHealth }) {
  const healthStyle = healthColors[health.healthStatus];
  const circumference = 2 * Math.PI * 40;
  const progress = (health.healthScore / 100) * circumference;

  return (
    <div className="rounded-xl border border-border bg-card p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Brain className="h-5 w-5 text-primary" />
          <h3 className="font-semibold text-card-foreground">AI Health Check</h3>
        </div>
        <span
          className={cn(
            "text-xs px-2 py-1 rounded-full font-medium",
            healthStyle.bg,
            healthStyle.text
          )}
        >
          {healthStyle.label}
        </span>
      </div>

      <div className="flex items-center gap-6">
        <div className="relative h-24 w-24 shrink-0">
          <svg className="h-full w-full -rotate-90" viewBox="0 0 100 100">
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="currentColor"
              strokeWidth="8"
              className="text-secondary"
            />
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="currentColor"
              strokeWidth="8"
              strokeDasharray={circumference}
              strokeDashoffset={circumference - progress}
              strokeLinecap="round"
              className={cn(
                "transition-all duration-1000 ease-out",
                health.healthScore >= 70
                  ? "text-green-500"
                  : health.healthScore >= 50
                    ? "text-yellow-500"
                    : "text-red-500"
              )}
            />
          </svg>
          <div className="absolute inset-0 flex items-center justify-center">
            <span className="text-xl font-bold text-card-foreground">
              {health.healthScore}
            </span>
          </div>
        </div>

        <div className="flex-1 grid grid-cols-2 gap-3">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-destructive shrink-0" />
            <span className="text-sm text-muted-foreground">
              {health.criticalIssues} Critical
            </span>
          </div>
          <div className="flex items-center gap-2">
            <AlertCircle className="h-4 w-4 text-yellow-500 shrink-0" />
            <span className="text-sm text-muted-foreground">
              {health.warnings} Warnings
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Lightbulb className="h-4 w-4 text-blue-500 shrink-0" />
            <span className="text-sm text-muted-foreground">
              {health.suggestions} Tips
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-muted-foreground shrink-0" />
            <span className="text-sm text-muted-foreground">
              Risk: {health.timelineRisk}
            </span>
          </div>
        </div>
      </div>

      <p className="text-sm text-muted-foreground mt-4 text-center">
        {health.summary}
      </p>
    </div>
  );
}

function TimelinePredictionCard({
  prediction,
}: {
  prediction: AITimelinePrediction;
}) {
  if (!prediction) return null;

  const riskStyle = riskColors[prediction.riskLevel];
  const RiskIcon = riskStyle.icon;

  return (
    <div className="rounded-lg border border-border bg-card p-4">
      <div className="flex items-center gap-2 mb-3">
        <Target className="h-5 w-5 text-primary" />
        <h4 className="font-semibold text-card-foreground">Timeline Prediction</h4>
      </div>

      <div
        className={cn(
          "flex items-center gap-2 p-3 rounded-lg mb-3",
          riskStyle.bg
        )}
      >
        <RiskIcon className={cn("h-5 w-5", riskStyle.text)} />
        <div>
          <p className={cn("font-medium text-sm", riskStyle.text)}>
            {prediction.riskLevel.charAt(0).toUpperCase() + prediction.riskLevel.slice(1)} Risk
          </p>
          <p className="text-xs text-muted-foreground">
            {Math.round(prediction.confidence * 100)}% confidence
          </p>
        </div>
      </div>

      {prediction.factors.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-medium text-muted-foreground mb-1">Factors:</p>
          <ul className="text-xs text-muted-foreground space-y-1">
            {prediction.factors.map((factor, index) => (
              <li key={index} className="flex items-start gap-1">
                <span className="text-primary mt-0.5">•</span>
                {factor}
              </li>
            ))}
          </ul>
        </div>
      )}

      {prediction.recommendations.length > 0 && (
        <div>
          <p className="text-xs font-medium text-muted-foreground mb-1">Recommendations:</p>
          <ul className="text-xs text-muted-foreground space-y-1">
            {prediction.recommendations.map((rec, index) => (
              <li key={index} className="flex items-start gap-1">
                <span className="text-green-500 mt-0.5">✓</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export function AIWorkflowPanel({ eventId, className }: AIWorkflowPanelProps) {
  const [analysis, setAnalysis] = useState<AIWorkflowAnalysis | null>(null);
  const [health, setHealth] = useState<AIWorkflowHealth | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [activeTab, setActiveTab] = useState<"insights" | "priorities" | "timeline">(
    "insights"
  );

  const fetchData = async () => {
    setIsLoading(true);
    try {
      const [analysisData, healthData] = await Promise.all([
        getAIWorkflowAnalysis(eventId),
        getWorkflowHealth(eventId),
      ]);
      setAnalysis(analysisData);
      setHealth(healthData);
    } catch (error) {
      console.error("Failed to fetch AI workflow analysis:", error);
      toast.error("Failed to load AI analysis");
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefresh = async () => {
    setIsRefreshing(true);
    try {
      await fetchData();
      toast.success("AI analysis refreshed");
    } catch (error) {
      console.error("Failed to refresh AI analysis:", error);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [eventId]);

  if (isLoading) {
    return (
      <div className={cn("rounded-xl border border-border bg-card p-6", className)}>
        <div className="flex items-center gap-2 mb-4">
          <Brain className="h-5 w-5 text-primary animate-pulse" />
          <h3 className="font-semibold text-card-foreground">AI Analysis</h3>
        </div>
        <div className="space-y-4 animate-pulse">
          <div className="h-24 bg-secondary rounded-lg" />
          <div className="h-32 bg-secondary rounded-lg" />
          <div className="h-20 bg-secondary rounded-lg" />
        </div>
      </div>
    );
  }

  const criticalInsights = analysis?.insights.filter(
    (i) => i.impact === "critical" || i.impact === "high"
  ) || [];

  return (
    <div className={cn("space-y-4", className)}>
      {/* Health Score Card */}
      {health && <HealthScoreCard health={health} />}

      {/* Main AI Panel */}
      <div className="rounded-xl border border-border bg-card overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between px-4 py-3 border-b border-border bg-secondary/30">
          <div className="flex items-center gap-2">
            <Brain className="h-5 w-5 text-primary" />
            <h3 className="font-semibold text-card-foreground">AI Workflow Insights</h3>
            {criticalInsights.length > 0 && (
              <span className="flex items-center gap-1 text-xs px-2 py-0.5 rounded-full bg-destructive/20 text-destructive">
                <AlertTriangle className="h-3 w-3" />
                {criticalInsights.length} Action Needed
              </span>
            )}
          </div>
          <button
            onClick={handleRefresh}
            disabled={isRefreshing}
            className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <RefreshCw
              className={cn("h-4 w-4", isRefreshing && "animate-spin")}
            />
            {isRefreshing ? "Refreshing..." : "Refresh"}
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-border">
          {[
            { id: "insights", label: "Insights", count: analysis?.insights.length },
            { id: "priorities", label: "Priority AI", count: analysis?.priorityRecommendations.length },
            { id: "timeline", label: "Timeline", count: null },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as typeof activeTab)}
              className={cn(
                "flex-1 px-4 py-3 text-sm font-medium transition-colors",
                activeTab === tab.id
                  ? "text-primary border-b-2 border-primary bg-primary/5"
                  : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
              )}
            >
              {tab.label}
              {tab.count !== null && tab.count > 0 && (
                <span className="ml-1 text-xs text-muted-foreground">
                  ({tab.count})
                </span>
              )}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="p-4 max-h-[400px] overflow-y-auto">
          {activeTab === "insights" && (
            <div className="space-y-3">
              {analysis?.insights && analysis.insights.length > 0 ? (
                analysis.insights.map((insight, index) => (
                  <InsightCard
                    key={index}
                    insight={insight}
                    onClick={() => {
                      toast.info(insight.recommendation || "Review this insight");
                    }}
                  />
                ))
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Brain className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>No insights available yet</p>
                  <p className="text-sm">
                    Add more tasks to get AI-powered recommendations
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === "priorities" && (
            <div className="space-y-3">
              {analysis?.priorityRecommendations &&
              analysis.priorityRecommendations.length > 0 ? (
                analysis.priorityRecommendations.map((rec, index) => (
                  <PriorityRecommendationCard
                    key={index}
                    recommendation={rec}
                  />
                ))
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Target className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>No priority recommendations</p>
                  <p className="text-sm">
                    Your task priorities look well-balanced
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === "timeline" && (
            <div className="space-y-3">
              {analysis?.timelinePrediction ? (
                <TimelinePredictionCard prediction={analysis.timelinePrediction} />
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Clock className="h-12 w-12 mx-auto mb-3 opacity-50" />
                  <p>No timeline prediction available</p>
                  <p className="text-sm">
                    Add due dates to your tasks for timeline analysis
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
