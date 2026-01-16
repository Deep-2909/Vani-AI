import { useState, useEffect } from "react";
import { DashboardLayout } from "@/components/layout/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Database, Trash2, Plus } from "lucide-react";
import { getDatabaseSources, syncDatabaseSource, DatabaseSource } from "@/lib/api";
import { LinkDataSourceDialog } from "@/components/databases/LinkDataSourceDialog";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

const Databases = () => {
  const [databases, setDatabases] = useState<DatabaseSource[]>([]);
  const [isConnectDialogOpen, setIsConnectDialogOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchSources = async () => {
      setIsLoading(true);
      const response = await getDatabaseSources();
      if (response.data) {
        setDatabases(response.data);
      }
      setIsLoading(false);
    };
    fetchSources();
  }, []);

  const handleDeleteDatabase = (id: string) => {
    setDatabases((prev) => prev.filter((db) => db.id !== id));
    toast.success("Database source removed successfully");
  };

  const handleSyncSource = async (data: any) => {
    const response = await syncDatabaseSource(
      data.datasetName,
      data.sourceType,
      data.connectionString
    );

    if (response.data) {
      toast.success(`Successfully synced ${data.datasetName} with Sahayaki!`);
      // Refresh the list
      const sourcesResponse = await getDatabaseSources();
      if (sourcesResponse.data) {
        setDatabases(sourcesResponse.data);
      }
    } else {
      toast.error(response.error || "Failed to sync database");
    }

    setIsConnectDialogOpen(false);
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Databases</h1>
            Manage live datasets and scheme information for Vani AI.
          </div>

        </div>

        {/* Database Sources */}
        <div className="space-y-6">
          {databases.map((database) => (
            <Card key={database.id} className="glass-card border-accent/20 overflow-hidden">
              {/* Database Header */}
              <div className="p-6 border-b border-border/50">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                      <Database className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <h3 className="font-semibold text-lg text-foreground">
                        {database.name}
                      </h3>
                      <Badge
                        className={cn(
                          "mt-1",
                          database.status === "active"
                            ? "bg-success/10 text-success border-success/30"
                            : "bg-muted text-muted-foreground"
                        )}
                      >
                        <span
                          className={cn(
                            "w-2 h-2 rounded-full mr-2",
                            database.status === "active" ? "bg-success" : "bg-muted-foreground"
                          )}
                        />
                        {database.status === "active" ? "ACTIVE STORE" : "INACTIVE"}
                      </Badge>
                    </div>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-muted-foreground hover:text-destructive"
                    onClick={() => handleDeleteDatabase(database.id)}
                  >
                    <Trash2 className="w-5 h-5" />
                  </Button>
                </div>
              </div>

              {/* Data Table */}
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow className="border-border hover:bg-transparent">
                      {database.columns.map((column) => (
                        <TableHead
                          key={column}
                          className="text-xs font-semibold text-muted-foreground uppercase tracking-wider"
                        >
                          {column}
                        </TableHead>
                      ))}
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {database.data && database.data.length > 0 ? (
                      database.data.map((record) => (
                        <TableRow
                          key={record.id}
                          className="border-border hover:bg-muted/30 transition-colors"
                        >
                          <TableCell className="text-sm font-medium text-foreground">
                            {record.ticketId}
                          </TableCell>
                          <TableCell className="text-sm text-foreground">
                            {record.date}
                          </TableCell>
                          <TableCell className="text-sm text-foreground">
                            {record.nameOfPerson}
                          </TableCell>
                          <TableCell className="text-sm text-foreground max-w-2xl">
                            {record.descriptionOfComplain}
                          </TableCell>
                          <TableCell className="text-sm text-foreground">
                            {record.department}
                          </TableCell>
                        </TableRow>
                      ))
                    ) : (
                      <TableRow>
                        <TableCell
                          colSpan={database.columns.length}
                          className="text-center text-muted-foreground py-8"
                        >
                          No data available
                        </TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            </Card>
          ))}

          {databases.length === 0 && (
            <Card className="glass-card p-12 text-center">
              <Database className="w-16 h-16 mx-auto mb-4 text-muted-foreground/30" />
              <h3 className="text-lg font-semibold text-foreground mb-2">
                No databases connected
              </h3>
              <p className="text-sm text-muted-foreground mb-6">
                Connect a new data source to get started
              </p>
              <Button onClick={() => setIsConnectDialogOpen(true)} className="gap-2">
                <Plus className="w-4 h-4" />
                Connect New Source
              </Button>
            </Card>
          )}
        </div>
      </div>

      {/* Link Data Source Dialog */}
      <LinkDataSourceDialog
        open={isConnectDialogOpen}
        onOpenChange={setIsConnectDialogOpen}
        onSync={handleSyncSource}
      />
    </DashboardLayout>
  );
};

export default Databases;
