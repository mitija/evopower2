/** @odoo-module **/

import {
    registerPatch
} from "@mail/model/model_core";
import {
    attr
} from "@mail/model/model_field";
import {
    clear
} from '@mail/model/model_field_command';

registerPatch({
    name: 'Attachment',
    fields: {
        access_token: attr(),
        isMsOffice: attr({
            compute() {
                const MsOfficetypes = [
                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    'application/msword',
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    'application/vnd.ms-excel',
                    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
                    'application/vnd.ms-powerpoint'
                ];
                return MsOfficetypes.includes(this.mimetype);
            },
        }),
        threadsAsAttachmentsInWebClientView: {
            compute() {
                return (this.isPdf || this.isImage || this.isMsOffice) && !this.isUploading ? this.allThreads : clear();
            }
        },
        isViewable: {
            compute() {
                return this._super() || this.isMsOffice;
            },
        },
        access_token: attr()
    },
});

registerPatch({
    name: "AttachmentViewerViewable",
    fields: {
        isMsOffice: attr({
            compute() {
                return this.attachmentOwner.isMsOffice;
            },
        }),
        attachmentId: attr({
            compute() {
                return this.attachmentOwner.id;
            },
        }),
        attachmentToken: attr({
            compute() {
                return this.attachmentOwner.access_token;
            },
        }),
    }
});