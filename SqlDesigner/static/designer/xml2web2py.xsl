<xsl:stylesheet version = '1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
	<xsl:template match="/sql">
		<html>
		<body id="body">
		<xsl:for-each select="table">
			<xsl:text>db.define_table("</xsl:text>
			<xsl:value-of select="@title" />
			<xsl:text>"</xsl:text>
			<xsl:for-each select="row">
                        <xsl:if test="not(title='id')">                       
				<xsl:text>,
    SQLField("</xsl:text>
				<xsl:value-of select="title" />
				<xsl:text>","</xsl:text>
				<xsl:value-of select="type" />
				<xsl:text>"</xsl:text>
                                <xsl:if test="@special!=''">
  				  <xsl:text>,length=</xsl:text>
                                  <xsl:value-of select="@special" />
                                </xsl:if>
				<xsl:if test="@nn">
					<xsl:text>,notnull=True</xsl:text>
				</xsl:if> 

				<xsl:choose>
					<xsl:otherwise>
                                           <xsl:if test="type = 'integer' or type='double' or type='boolean'">
						<xsl:text>,default=</xsl:text>
						<xsl:value-of select="default" />
						<xsl:text></xsl:text>
</xsl:if>
                                           <xsl:if test="not(type = 'integer' or type='double' or type='boolean')">
						<xsl:text>,default="</xsl:text>
						<xsl:value-of select="default" />
						<xsl:text>"</xsl:text>
</xsl:if>
					</xsl:otherwise>
				</xsl:choose>
						<xsl:text>)</xsl:text>
                        </xsl:if>
			</xsl:for-each>
			<xsl:text>)

</xsl:text>
		</xsl:for-each>
		</body>
		</html>
	</xsl:template>

</xsl:stylesheet>



