<!--
	XML 2 MsSQL XSL transformation for WWW SQL Designer
	Version: 0.1 Beta
	Author: schliden@gmail.com
-->

<xsl:stylesheet version = '1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
	<xsl:template match="/sql">
		<html>
		<body id="body">
		<xsl:for-each select="table">
			<xsl:text>CREATE TABLE [</xsl:text>
			<xsl:value-of select="@title" />
			<xsl:variable name="table" select="@title"/>
			<xsl:text>] (</xsl:text>
			<xsl:for-each select="row">
				<xsl:text>[</xsl:text>
				<xsl:value-of select="title" />
				<xsl:text>] </xsl:text>

				<xsl:if test="type = 'Integer'">
					<xsl:text>[int]</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Byte'">
					<xsl:text>[tinyint]</xsl:text>
				</xsl:if>
				
				<xsl:if test="type = 'Decimal'">
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>)</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Single precision'">
					<xsl:text>[float]</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Double precision'">
					<xsl:text>[real]</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Char'">
					<xsl:text>char</xsl:text>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>)</xsl:text>
				</xsl:if>
				
				<xsl:if test="type = 'String'">
					<xsl:text>[varchar]</xsl:text>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>)</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Text'">
					<xsl:text>[text]</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Binary'">
					<xsl:text>[varbinary]</xsl:text>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>)</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'BLOB'">
					<xsl:text>[image]</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Date'">
					<xsl:text>[smalldatetime]</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Time'">
					<xsl:text>[smalldatetime]</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Datetime'">
					<xsl:text>[datetime]</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Timestamp'">
					<xsl:text>[timestamp]</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Enum'">
					<xsl:text>[sql_variant]</xsl:text>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>) </xsl:text>
				</xsl:if>

				<xsl:if test="type = 'Set'">
					<xsl:text>[sql_variant]</xsl:text>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>) </xsl:text>
				</xsl:if>

				<xsl:text> </xsl:text>

				<xsl:if test="@pk">
					<xsl:text>IDENTITY (1, 1) NOT </xsl:text>
				</xsl:if>

				<xsl:if test="@nn">
					<xsl:text>NOT </xsl:text>
				</xsl:if>

				<xsl:text>NULL </xsl:text>

				<xsl:if test="@pk">
					<xsl:text>CONSTRAINT PK_</xsl:text>
					<xsl:value-of select="$table" />
					<xsl:text>_</xsl:text>
					<xsl:value-of select="title" />
					<xsl:text> PRIMARY KEY </xsl:text>
				</xsl:if>
				
				<xsl:if test="not (position()=last())">
					<xsl:text>,
</xsl:text>
				</xsl:if>
			</xsl:for-each>

			<xsl:text>
) ON [PRIMARY]
GO

</xsl:text>
		</xsl:for-each>
		<xsl:for-each select="relation">
			<xsl:text>ALTER TABLE [</xsl:text>
			<xsl:variable name="table_PK" select="table_1"/>
			<xsl:variable name="table_FK" select="table_2"/>
			<xsl:variable name="row_PK" select="row_1"/>
			<xsl:variable name="row_FK" select="row_2"/>
			<xsl:for-each select="../table[@id=$table_FK]">
				<xsl:value-of select="@title" />
			</xsl:for-each>
			<xsl:text>] ADD FOREIGN KEY (</xsl:text>
			<xsl:for-each select="../table[@id=$table_FK]/row[@id=$row_FK]">
				<xsl:value-of select="title" />
			</xsl:for-each>
			<xsl:text>) REFERENCES [</xsl:text>
			<xsl:for-each select="../table[@id=$table_PK]">
				<xsl:value-of select="@title" />
			</xsl:for-each>
			<xsl:text>] (</xsl:text>
			<xsl:text>[</xsl:text>
			<xsl:for-each select="../table[@id=$table_PK]/row[@id=$row_PK]">
				<xsl:value-of select="title" />
			</xsl:for-each>
			<xsl:text>] )

</xsl:text>
		</xsl:for-each>
		<xsl:text>
GO
</xsl:text>
		</body>
		</html>
	</xsl:template>

</xsl:stylesheet>