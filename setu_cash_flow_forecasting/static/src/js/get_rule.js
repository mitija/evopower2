/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardFieldProps } from "@web/views/fields/standard_field_props";


const { Component,onMounted, onWillStart, useState, useEffect,useRef, onRendered } = owl;
var core = require('web.core');
var QWeb = core.qweb;
var _t = core._t;

export class ShowForcastingFormulaWidget extends Component {

      setup() {
            super.setup();
            onMounted(() => {
                // Find All Help From Page And Add Content To Popup
                 _.each($('.js_show_forcasting_formula'), function (k, v){
                    var isRTL = _t.database.parameters.direction === "rtl";

                    var content = JSON.parse($(k).attr('info'));
                    var options = {
                        content: function () {
                            var $content = $(QWeb.render('SetuShowForcastingFormulaPopOver', {content: content.content }));
                            return $content;
                        },
                        html: true,
                        placement: 'right',
                        title: 'Help',
                        trigger: 'focus',
                        delay: { "show": 0, "hide": 100 },
                        container: $(k).parent(),
                    };
                    $(k).popover(options);
                });
            });
        }
}
ShowForcastingFormulaWidget.template = "SetuShowForcastingFormula";
ShowForcastingFormulaWidget.props = {
    ...standardFieldProps,
};

registry.category("fields").add("show_forcasting_formula_widget", ShowForcastingFormulaWidget);
