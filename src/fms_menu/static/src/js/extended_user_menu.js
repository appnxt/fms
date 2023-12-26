/** @odoo-module **/
import { registry } from "@web/core/registry";
import { browser } from "@web/core/browser/browser";

function manualItem(env) {
    const manualURL = "https://empowers.feishu.cn/docx/doxcnYvh27faPAjG2ISTAcwONDb";
    return {
        type: "item",
        id: "manual",
        description: env._t("操作手册"),
        href: manualURL,
        callback: () => {
            browser.open(manualURL, "_blank");
        },
        sequence: 59,
    };
}

registry
    .category("user_menuitems")
    .add("manual", manualItem)
