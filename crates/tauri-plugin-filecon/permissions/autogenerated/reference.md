## Default Permission

Allows resolving file names to icon names (`resolve`) and loading icon SVGs (`icon`).
Reading files for magic-byte detection (`icon_for_path`) is not included; enable it with
`filecon:allow-icon-for-path`.

#### This default permission set includes the following:

- `allow-resolve`
- `allow-icon`

## Permission Table

<table>
<tr>
<th>Identifier</th>
<th>Description</th>
</tr>


<tr>
<td>

`filecon:allow-icon`

</td>
<td>

Enables the icon command without any pre-configured scope.

</td>
</tr>

<tr>
<td>

`filecon:deny-icon`

</td>
<td>

Denies the icon command without any pre-configured scope.

</td>
</tr>

<tr>
<td>

`filecon:allow-icon-for-path`

</td>
<td>

Enables the icon_for_path command without any pre-configured scope.

</td>
</tr>

<tr>
<td>

`filecon:deny-icon-for-path`

</td>
<td>

Denies the icon_for_path command without any pre-configured scope.

</td>
</tr>

<tr>
<td>

`filecon:allow-resolve`

</td>
<td>

Enables the resolve command without any pre-configured scope.

</td>
</tr>

<tr>
<td>

`filecon:deny-resolve`

</td>
<td>

Denies the resolve command without any pre-configured scope.

</td>
</tr>
</table>
