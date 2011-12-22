<xsl:stylesheet version = '1.0' xmlns:xsl='http://www.w3.org/1999/XSL/Transform'>
	<xsl:template match="/">
		<html>
		<body id="body">
		<xsl:text>&lt;?xml version="1.0" encoding="ISO-8859-1" standalone="no"?&gt;</xsl:text>
		<xsl:text>&lt;database name="NAME DATABASE" defaultIdMethod="native"&gt;</xsl:text>
		<xsl:for-each select="sql/table">
			<xsl:variable name="idtable">
				<xsl:value-of select="@id"/>
			</xsl:variable>
			<xsl:text>&lt;table name="</xsl:text>
			<xsl:value-of select="@title" />
			<xsl:text>" description="</xsl:text>
			<xsl:value-of select="@title" /> 
			<xsl:text> Table"&gt;</xsl:text>
			<xsl:for-each select="row">
	
				<xsl:text>&lt;column name="</xsl:text>
				<xsl:value-of select="title" />
				<xsl:text>" type="</xsl:text>

				
				<xsl:if test="type = 'Integer'">
					<xsl:text>INTEGER</xsl:text>
				</xsl:if> 
				
				<xsl:if test="type = 'Byte'">
					<xsl:text>TINYINT</xsl:text>
				</xsl:if> 

				<xsl:if test="type = 'Single precision'">
					<xsl:text>FLOAT</xsl:text>
				</xsl:if> 

				<xsl:if test="type = 'Double precision'">
					<xsl:text>DOUBLE</xsl:text>
				</xsl:if> 

				<xsl:if test="type = 'Decimal'">
					<xsl:text>DECIMAL</xsl:text>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>)</xsl:text>
				</xsl:if>
				
				<xsl:if test="type = 'Char'">
					<xsl:text>CHAR</xsl:text>
					<xsl:text> (</xsl:text>
					<xsl:value-of select="@special" />
					<xsl:text>)</xsl:text>
				</xsl:if>


				<xsl:if test="type = 'String'">
					<xsl:text>VARCHAR</xsl:text>
					<xsl:text>" size="</xsl:text>
					<xsl:value-of select="@special" />
				</xsl:if> 

				<xsl:if test="type = 'Text'">
					<xsl:text>MEDIUMTEXT</xsl:text>
				</xsl:if> 

				<xsl:if test="type = 'Binary'">
					<xsl:text>VARBINARY</xsl:text>
					<xsl:text>" size="</xsl:text>
					<xsl:value-of select="@special" />
				</xsl:if> 

				<xsl:if test="type = 'BLOB'">
					<xsl:text>BLOB</xsl:text>
				</xsl:if> 

				<xsl:if test="type = 'Date'">
					<xsl:text>DATE</xsl:text>
				</xsl:if> 

				<xsl:if test="type = 'Time'">
					<xsl:text>TIME</xsl:text>
				</xsl:if> 

				<xsl:if test="type = 'Datetime'">
					<xsl:text>DATETIME</xsl:text>
				</xsl:if> 

				<xsl:if test="type = 'Timestamp'">
					<xsl:text>TIMESTAMP</xsl:text>
				</xsl:if> 

				<xsl:if test="type = 'Enum'">
					<xsl:text>ENUM</xsl:text>
					<xsl:text>" size="</xsl:text>
					<xsl:value-of select="@special" />
				</xsl:if> 

				<xsl:if test="type = 'Set'">
					<xsl:text>SET</xsl:text>
					<xsl:text>" size="</xsl:text>
					<xsl:value-of select="@special" />
				</xsl:if>

				<xsl:text>" primaryKey="</xsl:text>
	                        <xsl:choose>
				     <xsl:when test="@pk">
				     <xsl:text>true" autoIncrement="true</xsl:text>
				     </xsl:when>
				     <xsl:otherwise>
			             <xsl:text>false</xsl:text>
				     </xsl:otherwise>
				 </xsl:choose>

				 <xsl:text>" required="</xsl:text>
				 <xsl:choose>
				     	<xsl:when test="@nn">
					     <xsl:text>false</xsl:text>
				     	</xsl:when>
					<xsl:otherwise>
					     <xsl:text>true</xsl:text>
					</xsl:otherwise>															                                  </xsl:choose>

				
				<xsl:text>"/&gt; </xsl:text>

			</xsl:for-each>
			<xsl:for-each select="//sql/relation[table_2 = $idtable]">
				<xsl:variable name="idforeigntable">
					<xsl:value-of select="table_1" />
				</xsl:variable>
				<xsl:variable name="idforeignrow">
					<xsl:value-of select="row_1" />
				</xsl:variable>
				<xsl:variable name="idlocalrow">
					<xsl:value-of select="row_2" />
				</xsl:variable>

	                       	<xsl:text>&lt;foreign-key foreignTable="</xsl:text>
				<xsl:value-of select="//sql/table[@id = $idforeigntable]/@title" />
				<xsl:text>"&gt;&lt;reference local="</xsl:text>
				<xsl:value-of select="//sql/table[@id = $idtable]/row[@id = $idlocalrow]/title" />
				<xsl:text>" foreign="</xsl:text>
				<xsl:value-of select="//sql/table[@id = $idforeigntable]/row[@id = $idforeignrow]/title" />
				<xsl:text>"/&gt; &lt;/foreign-key&gt;</xsl:text>
			</xsl:for-each>

			<xsl:text>&lt;/table&gt;</xsl:text>
		</xsl:for-each>
		<xsl:text>&lt;/database&gt;</xsl:text>

		</body>
		</html>
	</xsl:template>

</xsl:stylesheet>
