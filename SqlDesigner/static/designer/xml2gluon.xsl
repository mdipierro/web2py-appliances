<xsl:stylesheet version = '1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
	<xsl:template match="/sql">
		<html>
		<body id="body">
		<xsl:for-each select="table">
			<xsl:text>db.define_table('</xsl:text>
			<xsl:value-of select="@title" />
			<xsl:variable name="table" select="@title"/>
			<xsl:text>',</xsl:text>
			<xsl:for-each select="row">
				<xsl:text>SQLField('</xsl:text>
				<xsl:value-of select="title" />
				<xsl:text>',</xsl:text>

				<xsl:if test="type = 'Integer'">
					<xsl:text>'integer'</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'boolean'">
					<xsl:text>'boolean'</xsl:text>
				</xsl:if>
				
				<xsl:if test="type = 'double'">
					<xsl:text>'double'</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'String'">
					<xsl:text>'string'</xsl:text>
					<xsl:text>,length=</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text></xsl:text>
				</xsl:if>

				<xsl:if test="type = 'upload'">
					<xsl:text>'upload'</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'boolean'">
					<xsl:text>'boolean'</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'blob'">
					<xsl:text>'blob'</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'date'">
					<xsl:text>'date'</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'time'">
					<xsl:text>'time'</xsl:text>
				</xsl:if>
				<xsl:if test="type = 'datetime'">
					<xsl:text>'datetime'</xsl:text>
				</xsl:if>

				<xsl:if test="type = 'set'">
					<xsl:text>'string'</xsl:text>
					<xsl:text>,requires=IS_IN_SET([</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>])</xsl:text>
				</xsl:if>

				<xsl:text>)</xsl:text>

				
				<xsl:if test="not (position()=last())">
					<xsl:text>,
</xsl:text>
				</xsl:if>
			</xsl:for-each>

			<xsl:text>)</xsl:text>
		</xsl:for-each>

		<xsl:for-each select="row">
				<xsl:choose>
					<xsl:when test="@pk">
						<xsl:text>,
</xsl:text>
						<xsl:text>PRIMARY KEY (</xsl:text>
						<xsl:value-of select="title" />
						<xsl:text>)</xsl:text>
					</xsl:when>
					<xsl:otherwise>
						<xsl:if test="@index">
							<xsl:text>,
</xsl:text>
							<xsl:text>KEY </xsl:text>
							<xsl:value-of select="title" />
							<xsl:text> (</xsl:text>
							<xsl:value-of select="title" />
							<xsl:text>)</xsl:text>
						</xsl:if>
					</xsl:otherwise>
				</xsl:choose>

			</xsl:for-each>
			<xsl:text>
);

</xsl:text>
		</xsl:for-each>

		</body>
		</html>
	</xsl:template>
</xsl:stylesheet>