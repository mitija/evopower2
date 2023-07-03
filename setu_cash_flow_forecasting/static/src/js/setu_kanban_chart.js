/** @odoo-module **/

import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
import { patch } from "@web/core/utils/patch";
var Registry = require('web.Registry');

patch(registry.category("fields").content.dashboard_graph[1].prototype, 'setu_cash_flow_forecasting', {
    renderChart() {
         if (this.chart) {
            this.chart.destroy();
        }
        let config;
        if(this.props.graphType === 'gauge'){
                         config = this._getGaugeChartConfig();

                  }
        if (this.props.graphType === "line") {
            config = this.getLineChartConfig();
        } else if (this.props.graphType === "bar") {
            config = this.getBarChartConfig();
        }
        this.chart = new Chart(this.canvasRef.el, config);
        // To perform its animations, ChartJS will perform each animation
        // step in the next animation frame. The initial rendering itself
        // is delayed for consistency. We can avoid this by manually
        // advancing the animation service.
        Chart.animationService.advance();
    },
    _getGaugeChartConfig () {
            var data = [];
            var labels = [];
            var backgroundColor = [];
            if(this.data[0].title === "dummy"){
                this.data[0].values.forEach(function (pt) {
                    data.push(pt.value);
                    labels.push(pt.label);
                    var color = pt.type === 'past' ? '#ccbdc8' : (pt.type === 'future' ? '#a5d8d7' : '#ebebeb');
                    backgroundColor.push(color);
                });
                return {
                    type: 'doughnut',
                    data: {
                        labels: ["No Forecast Calculated"],
                        datasets: [{
                            data: data,
                            backgroundColor: backgroundColor,
                        }],
                    },
                    options: {
                         title: {
                                display: true,
                                text: 'No Forecast Calculated'
                            },
                            legend: {
                                display: false
                            },
                        circumference: Math.PI,
                        rotation: -Math.PI,
                        tooltips: {
                            enabled: false
                        },
                    },
                }
            }
            else if(this.data[0].title === "zero-dummy"){
                this.data[0].values.forEach(function (pt) {
                    data.push(pt.value);
                    labels.push(pt.label);
                    var color = pt.type === 'past' ? '#ccbdc8' : (pt.type === 'future' ? '#a5d8d7' : '#ebebeb');
                    backgroundColor.push(color);
                });
                return {
                    type: 'doughnut',
                    data: {
                        labels: ["All Forested Values Are Zero"],
                        datasets: [{
                            data: data,
                            backgroundColor: backgroundColor,
                        }],
                    },
                    options: {
                         title: {
                                display: true,
                                text: 'All Forested Values Are Zero'
                            },
                            legend: {
                                display: false
                            },
                        circumference: Math.PI,
                        rotation: -Math.PI,
                        tooltips: {
                            enabled: false
                        },
                    },
                }
            }
            else{
                this.data[0].values.forEach(function (pt) {
                    data.push(pt.value);
                    labels.push(pt.label);
                    var color = pt.type === 'past' ? '#ccbdc8' : (pt.type === 'future' ? '#a5d8d7' : '#ebebeb');
                    backgroundColor.push(color);
                });
                return {
                    type: 'doughnut',
                    data: {
                        labels: labels,
                        datasets: [{
                            data: data,
                            backgroundColor: backgroundColor,
                        }],
                    },
                    options: {
                        circumference: Math.PI,
                        rotation: -Math.PI,
                        legend: {
                            display: false
                        },
                    },
                }
            }
        }
});

