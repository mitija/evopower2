/** @odoo-module alias=set.PivotView **/

import { PivotModel } from "@web/views/pivot/pivot_model";


PivotModel.prototype.getTable = function(tree, columns){

    const headers = this._getTableHeaders();
    const rows = this._getTableRows(this.data.rowGroupTree, headers[headers.length - 1]) ;
    var count_1 =  this.metaData.activeMeasures.length
    if (count_1 == 1){
        count_1 = 1
    }
    var i =0
    if(this.metaData.resModel == 'setu.cash.forecast' || this.metaData.resModel == 'setu.cash.forecast.report'){
        headers[0].splice(1);
        while(i<count_1){
            headers[headers.length - 1].pop()
            i++
        }
    }
    return {
        headers: headers,
        rows: rows,
    };
}
PivotModel.prototype._getTableRows = function(tree, columns){
        let rows = [];
        const group = tree.root;
        const rowGroupId = [group.values, []];
        const title = group.labels[group.labels.length - 1] || this.env._t("Total");
        const indent = group.labels.length;
        const isLeaf = !tree.directSubTrees.size;
        var count =  this.metaData.activeMeasures.length
        const rowGroupBys = this.metaData.fullRowGroupBys;
        const subGroupMeasurements = columns.map((column) => {
            const colGroupId = column.groupId;
            const groupIntersectionId = [rowGroupId[0], colGroupId[1]];
            const measure = column.measure;
            const originIndexes = column.originIndexes || [0];

            const value = this._getCellValue(groupIntersectionId, measure, originIndexes, {
                data: this.data,
            });

            const measurement = {
                groupId: groupIntersectionId,
                originIndexes: originIndexes,
                measure: measure,
                value: value,
                isBold: !groupIntersectionId[0].length || !groupIntersectionId[1].length,
            };
            return measurement;
        });
        if(this.metaData.resModel == 'setu.cash.forecast' || this.metaData.resModel == 'setu.cash.forecast.report'){
            if(subGroupMeasurements.length > 1)
            {
                var subGroupMeasurements_custom = subGroupMeasurements.slice(0, -count)
            }
            else
            {
                 var subGroupMeasurements_custom = subGroupMeasurements
            }
        }
        else
        {
            var subGroupMeasurements_custom = subGroupMeasurements
        }

        if(title != "Total"){
            rows.push({
                title: title,
                label:
                    indent === 0
                        ? undefined
                        : this.metaData.fields[rowGroupBys[indent - 1].split(":")[0]].string,
                groupId: rowGroupId,
                indent: indent,
                isLeaf: isLeaf,
                isFolded: isLeaf && rowGroupBys.length > group.values.length,
                //subGroupMeasurements : this.metaData.resModel == 'setu.cash.forecast' || this.metaData.resModel == 'setu.cash.forecast.report' && !
                //subGroupMeasurements.length == 1 ? subGroupMeasurements.slice(0, -count)  : subGroupMeasurements
                subGroupMeasurements: subGroupMeasurements_custom,
            });
        }

        const subTreeKeys = tree.sortedKeys || [...tree.directSubTrees.keys()];

        subTreeKeys.forEach((subTreeKey) => {
            const subTree = tree.directSubTrees.get(subTreeKey);
            rows = rows.concat(this._getTableRows(subTree, columns));
        });

        return rows;
}
