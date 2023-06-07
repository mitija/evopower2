/** @odoo-module **/
import { loadJS } from "@web/core/assets";
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";

const { Component,onMounted, onWillStart, useState, useEffect,useRef } = owl;

export class setu_cash_flow_forecasting_dashboard extends Component {
    setup() {
        super.setup();
        this.actionService = useService("action");

        this.orm = useService('orm');
        this.dashboardData = useState({});
        const context = Component.env.session.user_context;

        onWillStart(async () => {
            Object.assign(this.dashboardData, await this.orm.call(
                'setu.cash.flow.forecasting.dashboard',
                'get_dashboard_data',
                [], {
                    'context': context
                }));
            console.log(this.dashboardData)
            await loadJS("/web/static/lib/Chart/Chart.js")
        });
        onMounted(() => {
            this.on_attach_callback()
        });

    }
    // click event for toggle custom select dropdown menu = Done
    on_click_selectBtn(ev) {
        var select = $(ev.currentTarget)
        var selectDropdown = select.parent().find('.selectDropdown')
        if ($(selectDropdown).hasClass('toggle'))
            $(selectDropdown).removeClass('toggle')
        else
            $(selectDropdown).addClass('toggle')
    }

    on_attach_callback() {
        var self = this;
        // onchange methods for expense and income bar and line chart when change switch button configuration
        $('#switchBar').change(function() {
            self.setu_charts('expanse', 'bar', 'true');
        });
        $('#switchLine').change(function() {
            self.setu_charts('expanse', 'line', 'true');
        });
        $('#switchIncomeBar').change(function() {
            self.setu_charts('income', 'bar', 'true');
        });
        $('#switchIncomeLine').change(function() {
            self.setu_charts('income', 'line', 'true');
        });
        $('#switchValueChart').change(function() {

            $('.income_vs_expense_ratio').html('')
            self.income_vs_expense_value_chart('income_vs_expense_value')
            $('.switch_header_text').html('Cash In V/S Cash Out Forecasted Value')
            $('.switch_header_tooltip').html('Cash In V/S Cash Out Forecasted Value')
        });
        $('#switchRatioChart').change(function() {
            $('.income_vs_expense_value').html('')
            self.income_vs_expense_ratio_chart('income_vs_expense_ratio')
            $('.switch_header_text').html('Cash In V/S Cash Out Forecasted Ratio')
            $('.switch_header_tooltip').html('Cash In V/S Cash Out Forecasted Ratio')
        });

        // call card line chart method
        // this.dashboardData[10] : Cash-Out Line Chart
        // this.dashboardData[11] : Cash-In Line Chart
        self.card_line_chart('expansesChart', this.dashboardData[10]['month'], this.dashboardData[10]['total'], this.dashboardData[10]['currency'])
        self.card_line_chart('incomeChart', this.dashboardData[11]['month'], this.dashboardData[11]['total'], this.dashboardData[11]['currency'])

        // Call methods for generating line and bar chart for income and expense
        this.setu_charts('expanse', 'bar', 'false');
        this.setu_charts('income', 'bar', 'false');
        this.income_vs_expense_value_chart('income_vs_expense_value');

        //Call Filter Fiscal Period Method
        self.filterFiscalPeriod();

    }

    // Prepare line and bar chart data
    // this.dashboardData[2] : Cash-Out Forecast V/S Real Bar Chart
    // this.dashboardData[3] : Cash-In Forecast V/S Real Bar Chart
    // this.dashboardData[4] : Cash-Out Forecast V/S Real Line Chart
    // this.dashboardData[5] : Cash-In Forecast V/S Real Line Chart
    setu_charts(chart_id, chartType, isFilter) {
        var chart_data = this.dashboardData[1].chart_data;
        var month = [],
            income = [],
            expense = [],
            expanse_name = [],
            expanse_forecasted_value = [],
            expanse_real_value = [],
            expanse_month = [],
            income_name = [],
            income_forecasted_value = [],
            income_real_value = [],
            income_month = [];
        const monthNames = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEPT', 'OCT', 'NOV', 'DEC'];


        for (var data = 0; data < this.dashboardData[2].expense_chart_data.length; data++) {
            expanse_name.push(this.dashboardData[2].expense_chart_data[data].name[0].toUpperCase() + this.dashboardData[2].expense_chart_data[data].name.slice(1));
            console.log(this.dashboardData[2].expense_chart_data[data].forecast_value)
            expanse_forecasted_value.push(this.dashboardData[2].expense_chart_data[data].forecast_value);
            expanse_real_value.push(this.dashboardData[2].expense_chart_data[data].real_value);
            expanse_month.push(this.dashboardData[2].expense_chart_data[data].month);
        }
        for (var data = 0; data < this.dashboardData[3].income_chart_data.length; data++) {
            income_name.push(this.dashboardData[3].income_chart_data[data].name[0].toUpperCase() + this.dashboardData[3].income_chart_data[data].name.slice(1));
            debugger
            income_forecasted_value.push(this.dashboardData[3].income_chart_data[data].forecast_value);
            income_real_value.push(this.dashboardData[3].income_chart_data[data].real_value);
            income_month.push(this.dashboardData[3].income_chart_data[data].month);
        }
        var canvas = $('.' + chart_id).html("<canvas id=" + chart_id + " class='chart-canvas' height='400' />")
        var ctx = document.getElementById(chart_id).getContext("2d");

        var gradientStrokeViolet = ctx.createLinearGradient(0, 0, 0, 181);
        gradientStrokeViolet.addColorStop(0, 'rgba(218, 140, 255, 1)');
        gradientStrokeViolet.addColorStop(1, 'rgba(154, 85, 255, 1)');
        var gradientLegendViolet = 'linear-gradient(to right, rgba(218, 140, 255, 1), rgba(154, 85, 255, 1))';

        var gradientStrokeBlue = ctx.createLinearGradient(0, 0, 0, 360);
        gradientStrokeBlue.addColorStop(0, 'rgba(54, 215, 232, 1)');
        gradientStrokeBlue.addColorStop(1, 'rgba(177, 148, 250, 1)');

        var gradientStroke1 = ctx.createLinearGradient(0, 230, 0, 50);

        gradientStroke1.addColorStop(1, 'rgba(218, 140, 255, 1)');
        gradientStroke1.addColorStop(0.2, 'rgba(218, 140, 255, 0.2)');
        gradientStroke1.addColorStop(0, 'rgba(218, 140, 255, 0)');

        var ChartBackgroundColor1 = gradientStrokeViolet;
        var ChartBackgroundColor2 = gradientStrokeBlue;

        if (chartType == 'line') {
            ChartBackgroundColor1 = gradientStroke1;
            ChartBackgroundColor2 = gradientStroke1;
        }
        if (chart_id == 'income') {
            expanse_name = income_name;
            expanse_forecasted_value = income_forecasted_value;
            expanse_real_value = income_real_value;
            expanse_month = income_month;
        }

        var gradientLegendBlue = 'linear-gradient(to right, rgba(54, 215, 232, 1), rgba(177, 148, 250, 1))';
        if (isFilter == 'true') {
            if (chart_id == "income") {
                document.getElementById(chart_id).remove();
                $('#chart_income_expanse2').append('<canvas id=' + chart_id + ' class="chart-canvas" height="400"><canvas>');
                ctx = document.getElementById(chart_id).getContext("2d");
            } else {
                document.getElementById(chart_id).remove();
                $('#chart_income_expanse').append('<canvas id=' + chart_id + ' class="chart-canvas" height="400"><canvas>');
                ctx = document.getElementById(chart_id).getContext("2d");
            }
        }
        if (chartType == "line") {
            var dataset = []
            var dataset_data = []
            var line_labels = []
            if (chart_id == 'income') {
                for (var data = 0; data < this.dashboardData[5][0].length; data++) {
                    var dict = {};
                    dict["label"] = this.dashboardData[5][0][data]['name'][0].toUpperCase() + this.dashboardData[5][0][data]['name'].slice(1);
                    dict["data"] = this.dashboardData[5][0][data]['forecast_value'];
                    dict["type"] = 'line';
                    dict["borderColor"] = this.getRandomColor();
                    dict['legendColor'] = gradientLegendViolet;
                    dict['backgroundColor'] = ChartBackgroundColor1;
                    dict['fill'] = false;
                    dict['tension'] = 0.1;
                    dict['pointBorderWidth'] = 4,
                        dict['pointHoverRadius'] = 8,
                        dict['pointHoverBorderWidth'] = 5,
                        dict['pointRadius'] = 4,
                        dict['pointHitRadius'] = 16,
                        dataset.push(dict)
                }
                if (this.dashboardData[5][0].length > 0) {
                    line_labels = this.dashboardData[5][0][0]['forecast_period'];
                }
            } else {
                for (var data = 0; data < this.dashboardData[4][0].length; data++) {
                    var dict = {};
                    dict["label"] = this.dashboardData[4][0][data]['name'][0].toUpperCase() + this.dashboardData[4][0][data]['name'].slice(1);
                    dict["data"] = this.dashboardData[4][0][data]['forecast_value'];
                    dict["type"] = 'line';
                    dict["borderColor"] = this.getRandomColor();
                    dict['legendColor'] = gradientLegendViolet;
                    dict['backgroundColor'] = ChartBackgroundColor1;
                    dict['fill'] = false;
                    dict['tension'] = 0.1;
                    dict['pointBorderWidth'] = 4,
                        dict['pointHoverRadius'] = 8,
                        dict['pointHoverBorderWidth'] = 5,
                        dict['pointRadius'] = 4,
                        dict['pointHitRadius'] = 16,
                        dataset.push(dict)
                }
                if (this.dashboardData[4][0].length > 0) {
                    line_labels = this.dashboardData[4][0][0]['forecast_period'];
                }
            }
            var is_offset = false
            if (line_labels.length == 1) {
                is_offset = true
            }
            if (dataset.every(item => item['data'].length === 0)) {
                var myChart = new Chart(ctx, {
                    type: chartType,
                    data: {
                        labels: monthNames,
                        datasets: [{
                                label: 'Series 1',
                                data: [6, 10, 9, 6, 14, 12, 16, 13, 9, 7, 6, 10],
                                fill: false,
                                borderColor: '#dadada',
                                backgroundColor: '#dadada',
                                borderWidth: 2
                            },
                            {
                                label: 'Series 2',
                                data: [10, 8, 6, 5, 12, 8, 16, 17, 6, 7, 6, 10],
                                fill: false,
                                borderColor: '#dadada',
                                backgroundColor: '#dadada',
                                borderWidth: 2
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false,
                            }
                        },
                        interaction: {
                            intersect: false,
                            mode: 'index',
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                min: 0,
                                grid: {
                                    drawBorder: false,
                                    display: true,
                                    drawOnChartArea: true,
                                    drawTicks: false,
                                    borderDash: [5, 5]
                                },
                                ticks: {
                                    display: true,
                                    padding: 10,
                                    color: '#fbfbfb',
                                    font: {
                                        size: 11,
                                        family: "Open Sans",
                                        style: 'normal',
                                        lineHeight: 2
                                    },
                                }
                            },
                            x: {
                                grid: {
                                    drawBorder: false,
                                    display: false,
                                    drawOnChartArea: false,
                                    drawTicks: true,
                                    borderDash: [5, 5]
                                },
                                ticks: {
                                    display: true,
                                    color: '#ccc',
                                    padding: 20,
                                    font: {
                                        size: 11,
                                        family: "Open Sans",
                                        style: 'normal',
                                        lineHeight: 2
                                    },
                                }
                            },
                        },
                    },

                });

                $("#" + chart_id + "_no_data").addClass("d-block")
            } else {
                var myChart = new Chart(ctx, {
                    type: chartType,
                    data: {
                        labels: line_labels,
                        datasets: dataset,
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false,
                            }
                        },
                        interaction: {
                            intersect: false,
                            mode: 'index',
                        },
                        scales: {
                            xAxes: [{
                                offset: is_offset,
                                scaleLabel: {
                                    display: true,
                                    labelString: 'Fiscal Period',
                                    fontStyle: "bold",
                                },
                            }],

                            yAxes: [{
                                ticks: {
                                    beginAtZero: true
                                },
                                scaleLabel: {
                                    display: true,
                                    labelString: 'Value (' + this.dashboardData[12] + ')',
                                    fontStyle: "bold",
                                },
                            }],
                            y: {
                                beginAtZero: true,
                                min: 0,
                                grid: {
                                    drawBorder: false,
                                    display: true,
                                    drawOnChartArea: true,
                                    drawTicks: false,
                                    borderDash: [5, 5]
                                },
                                ticks: {
                                    display: true,
                                    padding: 10,
                                    color: '#fbfbfb',
                                    font: {
                                        size: 11,
                                        family: "Open Sans",
                                        style: 'normal',
                                        lineHeight: 2
                                    },
                                }
                            },
                            x: {
                                grid: {
                                    drawBorder: false,
                                    display: false,
                                    drawOnChartArea: false,
                                    drawTicks: true,
                                    borderDash: [5, 5]
                                },
                                ticks: {
                                    display: true,
                                    color: '#ccc',
                                    padding: 20,
                                    font: {
                                        size: 11,
                                        family: "Open Sans",
                                        style: 'normal',
                                        lineHeight: 2
                                    },
                                }
                            },
                        },
                    },

                });
                if ($("#" + chart_id + "_no_data").hasClass("d-block")) {
                    $("#" + chart_id + "_no_data").removeClass("d-block");
                }
                $("#" + chart_id + "_no_data").addClass("d-none")
            }
        } else {
            if (expanse_real_value.length == 0 || expanse_forecasted_value.length == 0) {
                var myChart = new Chart(ctx, {
                    type: chartType,
                    data: {
                        labels: monthNames,
                        datasets: [{
                                label: "Forecasted Value",
                                backgroundColor: "#dadada",
                                borderWidth: 1,
                                borderColor: "#dadada",
                                fill: false,
                                data: [6, 10, 9, 6, 14, 12, 16, 13, 9, 7, 6, 10]
                            },
                            {
                                label: "Real Value",
                                backgroundColor: "#dadada",
                                borderWidth: 1,
                                borderColor: "#dadada",
                                fill: false,
                                data: [10, 8, 6, 5, 12, 8, 16, 17, 6, 7, 6, 10]
                            }
                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false,
                            }
                        },
                        interaction: {
                            intersect: false,
                            mode: 'index',
                        },
                        tooltips: {
                            enabled: false
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                min: 0,
                                grid: {
                                    drawBorder: false,
                                    display: true,
                                    drawOnChartArea: true,
                                    drawTicks: false,
                                    borderDash: [5, 5]
                                },
                                ticks: {
                                    display: true,
                                    padding: 10,
                                    color: '#fbfbfb',
                                    font: {
                                        size: 11,
                                        family: "Open Sans",
                                        style: 'normal',
                                        lineHeight: 2
                                    },
                                }
                            },
                            x: {
                                grid: {
                                    drawBorder: false,
                                    display: false,
                                    drawOnChartArea: false,
                                    drawTicks: true,
                                    borderDash: [5, 5]
                                },
                                ticks: {
                                    display: true,
                                    color: '#ccc',
                                    padding: 20,
                                    font: {
                                        size: 11,
                                        family: "Open Sans",
                                        style: 'normal',
                                        lineHeight: 2
                                    },
                                }
                            },
                        },
                    },

                });
                if ($("#" + chart_id + "_no_data").hasClass("d-none")) {
                    $("#" + chart_id + "_no_data").removeClass("d-none");
                }
                $("#" + chart_id + "_no_data").addClass("d-block")
            } else {
                var chart_label = ""
                if (chart_id == 'expanse') {
                    chart_label = "Cash Out Type"
                } else {
                    chart_label = "Cash In Type"
                }
                var myChart = new Chart(ctx, {
                    type: chartType,
                    data: {
                        labels: expanse_name,
                        datasets: [{
                                label: "Forecasted Value",
                                borderColor: gradientStrokeViolet,
                                backgroundColor: ChartBackgroundColor1,
                                legendColor: gradientLegendViolet,
                                fill: true,
                                data: expanse_forecasted_value,
                                tension: 0.4,
                                pointRadius: 0,
                            },
                            {
                                label: 'Real Value',
                                borderColor: gradientStrokeBlue,
                                backgroundColor: ChartBackgroundColor2,
                                legendColor: gradientStrokeBlue,
                                fill: true,
                                data: expanse_real_value,
                                tension: 0.4,
                                pointRadius: 0,
                            },

                        ]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false,
                            }
                        },
                        interaction: {
                            intersect: false,
                            mode: 'index',
                        },
                        scales: {
                            xAxes: [{
                                scaleLabel: {
                                    display: true,
                                    labelString: chart_label,
                                    fontStyle: "bold",
                                }
                            }],
                            yAxes: [{
                                ticks: {
                                    beginAtZero: true
                                },
                                scaleLabel: {
                                    display: true,
                                    labelString: 'Value (' + this.dashboardData[12] + ')',
                                    fontStyle: "bold",
                                }
                            }],
                            y: {
                                beginAtZero: true,
                                suggestedMin: 0,
                                min: 0,
                                grid: {
                                    drawBorder: false,
                                    display: true,
                                    drawOnChartArea: true,
                                    drawTicks: false,
                                    borderDash: [5, 5]
                                },
                                ticks: {
                                    display: true,
                                    padding: 10,
                                    color: '#fbfbfb',
                                    font: {
                                        size: 11,
                                        family: "Open Sans",
                                        style: 'normal',
                                        lineHeight: 2
                                    },
                                }
                            },
                            x: {
                                grid: {
                                    drawBorder: false,
                                    display: false,
                                    drawOnChartArea: false,
                                    drawTicks: true,
                                    borderDash: [5, 5]
                                },
                                ticks: {
                                    display: true,
                                    color: '#ccc',
                                    padding: 20,
                                    font: {
                                        size: 11,
                                        family: "Open Sans",
                                        style: 'normal',
                                        lineHeight: 2
                                    },
                                }
                            },
                        },
                    },

                })
                if ($("#" + chart_id + "_no_data").hasClass("d-block")) {
                    $("#" + chart_id + "_no_data").removeClass("d-block");
                }
                $("#" + chart_id + "_no_data").addClass("d-none")
            }
        }
    }
    // Card Line Chart Method
    card_line_chart(chart_id, month, total, currency) {
        var self = this;
        var canvas = $('.' + chart_id).html("<canvas id=" + chart_id + " class='chart-canvas pt' height='400' />")
        var display_data = currency;
        var ctx = document.getElementById(chart_id).getContext("2d");

        var gradientStrokeViolet = ctx.createLinearGradient(0, 0, 0, 181);
        gradientStrokeViolet.addColorStop(0, 'rgba(218, 140, 255, 1)');
        gradientStrokeViolet.addColorStop(1, 'rgba(154, 85, 255, 1)');
        var gradientLegendViolet = 'linear-gradient(to right, rgba(218, 140, 255, 1), rgba(154, 85, 255, 1))';
        var is_offset = false
        if (month.length == 1) {
            is_offset = true
        }
        var myChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: month,
                datasets: [{
                    data: total,
                    fill: true,
                    borderColor: gradientStrokeViolet,
                    //backgroundColor: gradientStrokeViolet,
                    pointBorderWidth: 4,
                    pointHoverRadius: 8,
                    pointHoverBackgroundColor: gradientStrokeViolet,
                    pointHoverBorderColor: gradientStrokeViolet,
                    pointHoverBorderWidth: 5,
                    pointRadius: 4,
                    pointHitRadius: 16,

                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                tooltips: {
                    callbacks: {
                        label: function(tooltipItem) {
                            return " " + display_data[tooltipItem.index];
                        }
                    }
                },
                legend: {
                    position: "bottom",
                    display: false
                },
                scales: {
                    xAxes: [{
                        offset: is_offset,
                        scaleLabel: {
                            display: true,
                            labelString: 'Fiscal Period',
                            fontStyle: "bold",
                        }
                    }],
                    yAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: 'Value (' + this.dashboardData[12] + ')',
                            fontStyle: "bold",
                        },
                        ticks: {
                            beginAtZero: true,
                        }
                    }],

                },
            },
        });

    }
    // Prepare Income Vs Expense Value Chart
    // self.dashboardData[13] : Cash In V/S Cash Out Forecasted Value
    income_vs_expense_value_chart(chart_id) {

        var self = this;
        var canvas = $('.' + chart_id).html("<canvas id=" + chart_id + " class='chart-canvas pt' height='400' />")
        var ctx = document.getElementById(chart_id).getContext("2d");

        var gradientStrokeViolet = ctx.createLinearGradient(0, 0, 0, 181);
        gradientStrokeViolet.addColorStop(0, 'rgba(218, 140, 255, 1)');
        gradientStrokeViolet.addColorStop(1, 'rgba(154, 85, 255, 1)');
        var gradientLegendViolet = 'linear-gradient(to right, rgba(218, 140, 255, 1), rgba(154, 85, 255, 1))';

        var gradientStrokeBlue = ctx.createLinearGradient(0, 0, 0, 360);
        gradientStrokeBlue.addColorStop(0, 'rgba(54, 215, 232, 1)');
        gradientStrokeBlue.addColorStop(1, 'rgba(177, 148, 250, 1)');

        var period = []
        var data = []
        var income = []
        var expense = []
        for (var i = 0; i < self.dashboardData[13].length; i++) {
            period.push(Object.keys(self.dashboardData[13][i])[0])
            income.push(Object.values(self.dashboardData[13][i])[0][0])
            expense.push(Object.values(self.dashboardData[13][i])[0][1])
            //            data.push(Object.values(self.dashboardData[13][i])[0] )
        }

        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: period,
                datasets: [{
                        label: 'Cash In',
                        data: income,
                        fill: true,
                        borderColor: gradientStrokeViolet,
                        backgroundColor: gradientStrokeViolet,
                        pointBorderWidth: 4,
                        pointHoverRadius: 8,
                        pointHoverBackgroundColor: gradientStrokeViolet,
                        pointHoverBorderColor: gradientStrokeViolet,
                        pointHoverBorderWidth: 5,
                        pointRadius: 4,
                        pointHitRadius: 16,

                    },
                    {
                        label: 'Cash Out',
                        data: expense,
                        fill: true,
                        borderColor: gradientStrokeBlue,
                        backgroundColor: gradientStrokeBlue,
                        pointBorderWidth: 4,
                        pointHoverRadius: 8,
                        pointHoverBackgroundColor: gradientStrokeBlue,
                        pointHoverBorderColor: gradientStrokeBlue,
                        pointHoverBorderWidth: 5,
                        pointRadius: 4,
                        pointHitRadius: 16,

                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    display: true,
                },
                scales: {
                    xAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: 'Fiscal Period',
                            fontStyle: "bold",
                        }
                    }],
                    yAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: 'Ratio',
                            fontStyle: "bold",
                        },
                        ticks: {
                            beginAtZero: true,
                        }
                    }],

                },
            },
        });
    }

    // Prepare Income Vs Expense Ratio Chart
    // self.dashboardData[14] : Cash In V/S Cash Out Forecasted Ratio
    income_vs_expense_ratio_chart(chart_id) {

        var self = this;
        var canvas = $('.' + chart_id).html("<canvas id=" + chart_id + " class='chart-canvas pt' height='400' />")
        var ctx = document.getElementById(chart_id).getContext("2d");

        var gradientStrokeViolet = ctx.createLinearGradient(0, 0, 0, 181);
        gradientStrokeViolet.addColorStop(0, 'rgba(218, 140, 255, 1)');
        gradientStrokeViolet.addColorStop(1, 'rgba(154, 85, 255, 1)');
        var gradientLegendViolet = 'linear-gradient(to right, rgba(218, 140, 255, 1), rgba(154, 85, 255, 1))';

        var gradientStrokeBlue = ctx.createLinearGradient(0, 0, 0, 360);
        gradientStrokeBlue.addColorStop(0, 'rgba(54, 215, 232, 1)');
        gradientStrokeBlue.addColorStop(1, 'rgba(177, 148, 250, 1)');

        var period = []
        var data = []
        for (var i = 0; i < self.dashboardData[14].length; i++) {
            period.push(Object.keys(self.dashboardData[14][i])[0])
            data.push(Object.values(self.dashboardData[14][i])[0])
        }

        var myChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: period,
                datasets: [{
                    label: 'Ratio',
                    data: data,
                    fill: true,
                    borderColor: gradientStrokeViolet,
                    backgroundColor: gradientStrokeViolet,
                    pointBorderWidth: 4,
                    pointHoverRadius: 8,
                    pointHoverBackgroundColor: gradientStrokeViolet,
                    pointHoverBorderColor: gradientStrokeViolet,
                    pointHoverBorderWidth: 5,
                    pointRadius: 4,
                    pointHitRadius: 16,

                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                legend: {
                    display: true,
                },
                scales: {
                    xAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: 'Fiscal Period',
                            fontStyle: "bold",
                        }
                    }],
                    yAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: 'Ratio',
                            fontStyle: "bold",
                        },
                        ticks: {
                            beginAtZero: true,
                        }
                    }],

                },
            },
        });
    }
    // click event for selection option and refresh charts according to selected options
    on_click_option(ev) {
        var self = this;
        var option = $(ev.currentTarget)
        var selectBtn = option.parent().parent().parent().find('.selectBtn')
        var selectDropdown = option.parent().parent()

        if (option.html() != $(selectBtn).html()) {
            if (option[0].innerText != "Custom Fiscal Period") {

                //                await this.orm.call('setu.cash.flow.forecasting.dashboard', 'get_dashboard_data', [[[{"filter": option[0].innerText}]]]);
                this.orm.call('setu.cash.flow.forecasting.dashboard', 'get_dashboard_data', [
                    [{
                        "filter": option[0].innerText
                    }]
                ]).then((res) => {
                    self.dashboardData = res;
                    if ($(option).hasClass('option-cashout')) {
                        self.setu_charts('expanse', 'bar', 'false');
                    }
                    if ($(option).hasClass('option-cashin')) {
                        self.setu_charts('income', 'bar', 'false');
                        //self.setu_charts('expanse','bar','false');
                    }

                    $('#switchBar').prop("checked", true);
                    $('#switchIncomeBar').prop("checked", true);
                });

                //                var dashboard_data = self.rpc({
                //                    model: 'setu.cash.flow.forecasting.dashboard',
                //                    method: 'get_dashboard_data',
                //                    args: [[{"filter": option[0].innerText}]]
                //
                //                })
                //                .then(function (res) {
                //                   self.dashboardData = res;
                //                    if($(option).hasClass('option-cashout')){
                //                        self.setu_charts('expanse','bar','false');
                //                    }
                //                    if($(option).hasClass('option-cashin')){
                //                        self.setu_charts('income','bar','false');
                //                        //self.setu_charts('expanse','bar','false');
                //                    }
                //
                //                    $('#switchBar').prop("checked", true);
                //                    $('#switchIncomeBar').prop("checked", true);
                //                });
            }
        }
        $(selectBtn).html(option.html())
        $("#DashboardName").html(option.html())
        $(selectDropdown).removeClass('toggle')
        $('.current_filter_msg').html('')
        if ($(option).hasClass('option-cashin')) {
            $("#apply_filter").addClass('filter-option-cashin')
            $("#apply_filter").removeClass('filter-option-cashout')
        }
        if ($(option).hasClass('option-cashout')) {
            $("#apply_filter").removeClass('filter-option-cashin')
            $("#apply_filter").addClass('filter-option-cashout')
        }

    }
    // click event for open expanse list view = Done
    async on_click_view(ev) {
        var self = this;
        var view = $(ev.currentTarget).attr('data-view')
        console.log(view)
        self.actionService.doAction({
            name: 'Cash Forecast Report Analysis',
            type: 'ir.actions.act_window',
            res_model: 'setu.cash.forecast',
            target: 'current',
            views: [
                [false, 'list']
            ],
            domain: [
                ['forecast_type', '=', view]
            ],
        });
    }

    // generating random color foe charts
    getRandomColor() {
        var letters = '0123456789ABCDEF'.split('');
        var color = '#';
        for (var i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }

    // get data according to date filter
    filterFiscalPeriod() {
        var self = this;
        $('#apply_filter').on('click', function() {
            var StartDate = document.getElementById("filterFiscalPeriodStart");
            var EndDate = document.getElementById("filterFiscalPeriodEnd");
            if (EndDate.options[EndDate.selectedIndex] == null && StartDate.options[StartDate.selectedIndex] == null) {
                $("#filterAlert").html("Please Select Start Date And End Date");
                $("#filterAlert").slideDown(500)
                setTimeout(function() {
                    $("#filterAlert").slideUp(500)
                }, 4000);
            } else if (new Date(EndDate.options[EndDate.selectedIndex].getAttribute('end-date')) > new Date(StartDate.options[StartDate.selectedIndex].getAttribute('start-date'))) {
                self.orm.call('setu.cash.flow.forecasting.dashboard', 'get_dashboard_data', [
                    [{
                        "filter": "time_period"
                    }, {
                        "start_date": StartDate.options[StartDate.selectedIndex].getAttribute('start-date')
                    }, {
                        "end_date": EndDate.options[EndDate.selectedIndex].getAttribute('end-date')
                    }, ]
                ]).then((res) => {
                    self.dashboardData = res
                    if ($("#apply_filter").hasClass('filter-option-cashin')) {
                        console.log("filter-option-cashin")
                        self.setu_charts('income', 'bar', 'false');
                        $('#switchIncomeBar').prop("checked", true);
                        $('.option-cashin-message').html('Custom Fiscal Period ( ' + $('#filterFiscalPeriodStart').val() + ' To ' + $('#filterFiscalPeriodEnd').val() + ' )')
                    }
                    if ($("#apply_filter").hasClass('filter-option-cashout')) {
                        console.log("filter-option-cashout")
                        self.setu_charts('expanse', 'bar', 'false');
                        $('#switchBar').prop("checked", true);
                        $('.option-cashout-message').html('Custom Fiscal Period ( ' + $('#filterFiscalPeriodStart').val() + ' To ' + $('#filterFiscalPeriodEnd').val() + ' )')
                    }
                });
                $('#myModal').modal('hide');
            } else {
                $("#filterAlert").html("Please Select Proper Start Date OR End Date");
                $("#filterAlert").slideDown(500)
                setTimeout(function() {
                    $("#filterAlert").slideUp(500)
                }, 4000);
            }

        });
    }

    // Hide And Show tooltip-dialog in dashboard
    on_click_info_badge(ev) {

        $(ev.target.parentElement.parentElement).find('.tooltip-dialog').slideToggle(500);
        setTimeout(function() {
            $(ev.target.parentElement.parentElement).find('.tooltip-dialog').slideToggle(500)
        }, 4000);
    }

}

setu_cash_flow_forecasting_dashboard.template = 'SetuCashForecastDashboard';

registry.category('actions').add('setu_cash_flow_forecasting_dashboard', setu_cash_flow_forecasting_dashboard);