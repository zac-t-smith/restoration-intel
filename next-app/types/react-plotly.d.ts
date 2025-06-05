/**
 * Type declarations for react-plotly.js
 */

declare module 'react-plotly.js' {
  import * as React from 'react';
  import * as Plotly from 'plotly.js';

  interface PlotParams {
    data?: Array<Partial<Plotly.PlotData>>;
    layout?: Partial<Plotly.Layout>;
    config?: Partial<Plotly.Config>;
    frames?: Array<Partial<Plotly.Frame>>;
    useResizeHandler?: boolean;
    style?: React.CSSProperties;
    className?: string;
    onInitialized?: (figure: Plotly.Figure, graphDiv: HTMLElement) => void;
    onUpdate?: (figure: Plotly.Figure, graphDiv: HTMLElement) => void;
    onPurge?: (figure: Plotly.Figure, graphDiv: HTMLElement) => void;
    onError?: (err: Error) => void;
    onSelected?: (event: Plotly.PlotSelectionEvent) => void;
    onDeselect?: () => void;
    onSelecting?: (event: Plotly.PlotSelectionEvent) => void;
    onRestyle?: (data: any) => void;
    onRelayout?: (data: any) => void;
    onClickAnnotation?: (event: Plotly.ClickAnnotationEvent) => void;
    onAfterExport?: () => void;
    onAfterPlot?: () => void;
    onAnimated?: () => void;
    onAnimatingFrame?: (event: Plotly.FrameAnimationEvent) => void;
    onAnimationInterrupted?: () => void;
    onAutoSize?: () => void;
    onBeforeExport?: () => void;
    onButtonClicked?: (event: Plotly.ButtonClickEvent) => void;
    onClick?: (event: Plotly.PlotMouseEvent) => void;
    onClickSlice?: (event: Plotly.PlotMouseEvent) => void;
    onDoubleClick?: () => void;
    onHover?: (event: Plotly.PlotMouseEvent) => void;
    onLegendClick?: (event: Plotly.LegendClickEvent) => boolean;
    onLegendDoubleClick?: (event: Plotly.LegendClickEvent) => boolean;
    onRelayouting?: () => void;
    onRestyleStart?: () => void;
    onRestyleEnd?: () => void;
    onRedraw?: () => void;
    onSliderChange?: (event: Plotly.SliderChangeEvent) => void;
    onSliderEnd?: (event: Plotly.SliderEndEvent) => void;
    onSliderStart?: (event: Plotly.SliderStartEvent) => void;
    onTransitioning?: () => void;
    onTransitionInterrupted?: () => void;
    onUnhover?: (event: Plotly.PlotMouseEvent) => void;
    onWebGlContextLost?: () => void;
    divId?: string;
  }

  const Plot: React.FC<PlotParams>;
  export default Plot;
}

declare module 'plotly.js' {
  export interface PlotData {
    type: string;
    x: Array<any>;
    y: Array<any>;
    text: string | Array<string>;
    textinfo: string;
    textposition: string;
    hoverinfo: string;
    marker: {
      color: string | Array<string>;
    };
    line: {
      color: string;
      width: number;
    };
    name: string;
    mode: string;
  }

  export interface Layout {
    title: string | {
      text: string;
      font: {
        size: number;
        color?: string;
      };
    };
    autosize: boolean;
    width?: number;
    height?: number;
    margin: {
      l: number;
      r: number;
      t: number;
      b: number;
      pad?: number;
    };
    funnelmode?: string;
    funnelgap?: number;
    annotations?: Array<{
      x: number;
      y: number;
      xanchor: string;
      yanchor: string;
      text: string;
      showarrow: boolean;
      font?: {
        size: number;
        color: string;
      };
    }>;
  }

  export interface Config {
    responsive: boolean;
    displayModeBar: boolean;
  }

  export interface Frame {}
  export interface Figure {}
  export interface PlotSelectionEvent {}
  export interface ClickAnnotationEvent {}
  export interface FrameAnimationEvent {}
  export interface ButtonClickEvent {}
  export interface PlotMouseEvent {}
  export interface LegendClickEvent {}
  export interface SliderChangeEvent {}
  export interface SliderEndEvent {}
  export interface SliderStartEvent {}
}