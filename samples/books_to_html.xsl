<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="html" indent="yes"/>
    
    <xsl:template match="/">
        <html>
            <head>
                <title>Bookstore Catalog</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { color: #333; }
                    .book { border: 1px solid #ccc; margin: 10px 0; padding: 10px; border-radius: 5px; }
                    .title { font-size: 18px; font-weight: bold; color: #0066cc; }
                    .author { color: #666; font-style: italic; }
                    .price { color: #009900; font-weight: bold; }
                </style>
            </head>
            <body>
                <h1>Bookstore Catalog</h1>
                <xsl:apply-templates select="bookstore/book"/>
            </body>
        </html>
    </xsl:template>
    
    <xsl:template match="book">
        <div class="book">
            <div class="title">
                <xsl:value-of select="title"/>
                <xsl:text> (</xsl:text>
                <xsl:value-of select="@category"/>
                <xsl:text>)</xsl:text>
            </div>
            <div class="author">
                by <xsl:value-of select="author"/>
            </div>
            <div>Year: <xsl:value-of select="year"/></div>
            <div class="price">Price: $<xsl:value-of select="price"/></div>
            <div><xsl:value-of select="description"/></div>
        </div>
    </xsl:template>
</xsl:stylesheet>
