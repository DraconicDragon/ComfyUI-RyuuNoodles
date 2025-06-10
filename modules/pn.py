class HTMLDisplayNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "html_string": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "<b>Hello!</b>",
                    },
                ),
                "url_opt": (
                    "STRING",
                    {
                        "placeholder": "Optional URL to open in a new tab",
                    },
                ),
                "use_url": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "tooltip": "If checked, displays the page in the popup",
                    },
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "display_html"
    OUTPUT_NODE = True
    EXPERIMENTAL = True

    def display_html(self, html_string, url_opt, use_url):

        # No-op, handled in JS
        return (html_string,)
