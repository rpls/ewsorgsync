# Exchange EWS Calendar to Orgmode Synchronization

This is a simple tool for (one-way) synchronizing your EWS calendar to an
[org-mode](https://orgmode.org) file. The `ewsorgsync` command line tool will
read a configuration file (see `ewsorgsyncrc.example`) from `~/.ewsorgsyncrc`.

For regular synchronization use the provided systemd units. Install the
`ewsorgsync.{timer,service}` unit files to `~/.config/systemd/user/` and
activate the timer unit with `systemctl --user enable --now ewsorgsync.timer`.
By default, the timer unit will run every half hour, adapt the `OnBootSec`
and/or `OnUnitActiveSec` (or any other allowed options, see `man systemd.timer`)
options in the timer unit to your liking.
